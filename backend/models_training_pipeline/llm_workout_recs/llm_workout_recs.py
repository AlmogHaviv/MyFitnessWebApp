import textwrap
from typing import Dict, List
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from googleapiclient.discovery import build


class WorkoutRecommender:
    def __init__(self, user_profile: dict, query: str, youtube_api_key: str = "AIzaSyCyGZ_3m-GppNhk0nmps_rRay6f7B0hgGE"):
        self.user_profile = user_profile
        self.query = query
        self.youtube = build("youtube", "v3", developerKey=youtube_api_key)
        self.model = pipeline(model="declare-lab/flan-alpaca-gpt4-xl")

    def _call_llm(self, prompt: str, max_tokens: int = 150, retries: int = 2) -> str:
        for _ in range(retries):
            try:
                result = self.model(prompt, max_new_tokens=max_tokens, do_sample=True)
                response = result[0]["generated_text"].strip()
                if response:
                    return response
            except Exception as e:
                print(f"LLM call failed: {e}")
        return "[LLM output failed]"

    def _format_user_profile(self) -> str:
        return "\n".join(
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in self.user_profile.items() if value is not None
        )

    def _build_query_prompt(self) -> str:
        profile_str = self._format_user_profile()
        return textwrap.dedent(f"""
        You are an expert personal trainer helping users find relevant fitness videos on YouTube.

        User query: "{self.query}"

        User profile:
        {profile_str}

        Suggest a concise YouTube search query that focuses on the key exercises and goals.

        Output only the search query.
        """)

    def _build_explanation_prompt(self, title: str, description: str, transcript: str) -> str:
        return textwrap.dedent(f"""
        Analyze this fitness video and assess its usefulness for the user's goal.

        User goal: "{self.query}"

        Video Title: {title}
        Description: {description}
        Transcript Snippet: {transcript[:800]}

        Output the response in this format:

        EXPLANATION:
        - Why the video is helpful for the goal
        - Key points covered
        - Difficulty level

        EQUIPMENT:
        - List only essential workout equipment used in the video (one per line)

        Respond ONLY in the format shown above.
        """)

    def _get_transcript(self, video_id: str) -> str:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en'])
            return " ".join([entry['text'] for entry in transcript.fetch()])
        except Exception as e:
            print(f"Error getting transcript for video {video_id}: {e}")
            return ""

    def _search_youtube(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        try:
            response = self.youtube.search().list(
                q=query,
                part="snippet",
                type="video",
                maxResults=limit
            ).execute()

            results = []
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                description = item["snippet"].get("description", "")

                results.append({
                    "id": video_id,
                    "title": title,
                    "description": description
                })
            return results
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return []

    def _parse_llm_response(self, response: str) -> Dict[str, str]:
        try:
            if "EXPLANATION:" in response and "EQUIPMENT:" in response:
                explanation = response.split("EXPLANATION:")[1].split("EQUIPMENT:")[0].strip()
                equipment_block = response.split("EQUIPMENT:")[1].strip()
                equipment = [line.strip("-• ") for line in equipment_block.split("\n") if line.strip()]
                return {
                    "explanation": explanation,
                    "equipment": equipment
                }
            return {"explanation": response, "equipment": []}
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return {"explanation": response, "equipment": []}

    def workout_urls_and_explanations(self) -> List[Dict[str, str]]:
        print(f"Processing request: {self.query}")

        prompt = self._build_query_prompt()
        improved_query = self._call_llm(prompt, max_tokens=50)
        print(f"Improved query: {improved_query}")

        results = self._search_youtube(improved_query, limit=4)
        print(f"Found {len(results)} YouTube videos")

        recommendations = []
        for i, video in enumerate(results, 1):
            print(f"\nProcessing video {i}/{len(results)}")
            video_id = video["id"]
            title = video["title"]
            description = video["description"]
            transcript = self._get_transcript(video_id)

            explanation_prompt = self._build_explanation_prompt(title, description, transcript)
            llm_response = self._call_llm(explanation_prompt, max_tokens=200)
            print(f"Generated explanation for: {title}")

            parsed_response = self._parse_llm_response(llm_response)

            recommendations.append({
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "title": title,
                "explanation": parsed_response["explanation"],
                "equipment": parsed_response["equipment"]
            })

        return recommendations
