import textwrap
from typing import Dict, List
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, NoTranscriptAvailable
from transformers import pipeline
from googleapiclient.discovery import build
from concurrent.futures import ThreadPoolExecutor, as_completed

# we are not using this model due to space limitations in our PCs 

class WorkoutRecommender:
    def __init__(self, user_profile: dict, query: str, youtube_api_key: str = "AIzaSyCyGZ_3m-GppNhk0nmps_rRay6f7B0hgGE"):
        self.user_profile = user_profile
        self.query = query
        self.youtube = build("youtube", "v3", developerKey=youtube_api_key)
        self.model = pipeline(model="declare-lab/flan-alpaca-gpt4-xl")

    def _call_llm(self, prompt: str, max_tokens: int = 250, retries: int = 2) -> str:
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

        Suggest a concise Youtube query that focuses on the key exercises and goals.
        
        Use the user's profile to suggest a query.

        Output only the search query.
        """)

    def _build_explanation_prompt(self, title: str, description: str, transcript: str) -> str:
        # **Crucial change here:** Pass the transcript status to the LLM
        transcript_info = f"Transcript Snippet: {transcript[:800]}" if transcript else "Transcript: Not available. Please rely on Title and Description."

        return textwrap.dedent(f"""
        Analyze this fitness video and assess its usefulness for the user's goal.
        If the transcript is not available, analyze the video based on its title and description.

        User goal: "{self.query}"

        Video Title: {title}
        Description: {description}
        {transcript_info}

        Output the response in this format:

        EXPLANATION:
        - Why the video is helpful for the goal
        - Difficulty level

        EQUIPMENT:
        - List essential workout equipment used in the video (if mentioned or implied in title/description/transcript)

        Respond ONLY in the format shown above. If you cannot determine equipment, state "No specific equipment mentioned or implied."
        """)
    
    def _get_transcript(self, video_id: str) -> str:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # 1. Try to find a native English transcript directly
            try:
                transcript = transcript_list.find_transcript(['en'])
                return " ".join([entry['text'] for entry in transcript.fetch()])
            except NoTranscriptFound:
                pass  # No native English transcript, continue to translation attempts

            # 2. If no native English, try translating any available transcript to English
            for transcript in transcript_list:
                if transcript.is_translatable:
                    try:
                        translated = transcript.translate('en')
                        return " ".join([entry['text'] for entry in translated.fetch()])
                    except NoTranscriptAvailable:
                        print(f"No transcript available for translation of {transcript.language_code} for video {video_id}")
                    except Exception as te:
                        print(f"Failed to translate transcript {transcript.language_code} for video {video_id}: {te}")
                else:
                    print(f"Transcript in language {transcript.language_code} for video {video_id} is not translatable.")

            print(f"No usable transcript (native English or translatable) found for video {video_id}")
            # Return a specific message for the LLM
            return "No_Transcript_Available"

        except TranscriptsDisabled:
            print(f"Transcripts are disabled for video {video_id}.")
            # **Crucial change here:** Return a specific message for the LLM
            return "Transcripts_Disabled"
        except NoTranscriptFound:
            print(f"No transcripts found at all for video {video_id}.")
            # **Crucial change here:** Return a specific message for the LLM
            return "No_Transcript_Found_At_All"
        except Exception as e:
            print(f"An unexpected error occurred getting transcript for video {video_id}: {e}")
            # **Crucial change here:** Return a specific message for the LLM
            return f"Transcript_Error: {e}"

    def _search_youtube(self, query: str, limit: int = 2) -> List[Dict[str, str]]:
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

        def process_video(video: Dict[str, str]) -> Dict[str, str]:
            try:
                video_id = video["id"]
                title = video["title"]
                description = video["description"]
                transcript = self._get_transcript(video_id)

                explanation_prompt = self._build_explanation_prompt(title, description, transcript)
                llm_response = self._call_llm(explanation_prompt, max_tokens=250)
                print(f"Generated explanation for: {title}")

                parsed_response = self._parse_llm_response(llm_response)

                return {
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "title": title,
                    "explanation": parsed_response["explanation"],
                    "equipment": parsed_response["equipment"]
                }
            except Exception as e:
                print(f"Error processing video {video.get('title', 'unknown')}: {e}")
                return {}

        recommendations = []
        # Increased max_workers to 4 for potentially faster processing
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_video = {executor.submit(process_video, video): video for video in results}
            for future in as_completed(future_to_video):
                try:
                    result = future.result()
                    if result:
                        recommendations.append(result)
                except Exception as e:
                    # Catch exceptions from within process_video that were not handled there.
                    print(f"Error retrieving result from future: {e}")

        return recommendations