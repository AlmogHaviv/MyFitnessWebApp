import textwrap
from typing import Dict, List
from huggingface_hub import InferenceClient
from youtube_transcript_api import YouTubeTranscriptApi
from youtubesearchpython import VideosSearch

class WorkoutRecommender:
    def __init__(self, user_profile: Dict, query: str, hf_token: str = "put your hf token here"):
        self.user_profile = user_profile
        self.query = query
        self.model_id = "google/flan-t5-base"
        try:
            self.client = InferenceClient(model=self.model_id, token=hf_token)
        except Exception as e:
            print(f"Error initializing client: {e}")
            raise

    def _call_llm(self, prompt: str, max_tokens: int = 150) -> str:
        """Call the LLM with a prompt and return response text."""
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=max_tokens,
                temperature=0.7,
                top_p=0.95,
                repetition_penalty=1.15
            )
            return response.strip()
        except Exception as e:
            print(f"Error calling Hugging Face API: {e}")
            return ""

    def _format_user_profile(self) -> str:
        """Format user profile dictionary as readable string."""
        profile_str = []
        for key, value in self.user_profile.items():
            if value is not None:  # Only include non-None values
                formatted_key = key.replace('_', ' ').title()
                profile_str.append(f"{formatted_key}: {value}")
        return "\n".join(profile_str)

    def _build_query_prompt(self) -> str:
        profile_str = self._format_user_profile()
        return textwrap.dedent(f"""
        Task: Create a YouTube search query for fitness videos.
        
        User query: "{self.query}"
        
        User profile:
        {profile_str}
        
        Create a clear and specific search query that will find the best fitness videos for this user.
        Focus on the main exercise type and key terms.
        Return only the search query, nothing else.
        """)

    def _build_explanation_prompt(self, title: str, description: str, transcript: str) -> str:
        return textwrap.dedent(f"""
        Task: Analyze this fitness video.
        
        User goal: "{self.query}"
        
        Video details:
        Title: {title}
        Description: {description}
        Transcript: {transcript[:800]}
        
        Provide a detailed analysis in the following format:
        
        EXPLANATION:
        [Explain why this video is suitable for the user's goal, including difficulty level and key points covered]
        
        EQUIPMENT:
        [List all required equipment mentioned in the video, one per line]
        
        Keep the explanation clear and concise.
        """)

    def _get_transcript(self, video_id: str) -> str:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([entry['text'] for entry in transcript])
        except Exception as e:
            print(f"Error getting transcript: {e}")
            return ""

    def _search_youtube(self, query: str, limit: int = 5) -> list:
        try:
            search = VideosSearch(query, limit=limit)
            return search.result()["result"]
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return []

    def _parse_llm_response(self, response: str) -> Dict[str, str]:
        """Parse the LLM response into explanation and equipment sections."""
        try:
            # Split the response into sections
            sections = response.split("\n\n")
            explanation = ""
            equipment = []
            
            for section in sections:
                if section.startswith("EXPLANATION:"):
                    explanation = section.replace("EXPLANATION:", "").strip()
                elif section.startswith("EQUIPMENT:"):
                    # Get all lines after EQUIPMENT: and clean them
                    equipment_lines = section.replace("EQUIPMENT:", "").strip().split("\n")
                    equipment = [line.strip() for line in equipment_lines if line.strip()]
            
            return {
                "explanation": explanation,
                "equipment": equipment
            }
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return {
                "explanation": response,
                "equipment": []
            }

    def workout_urls_and_explanations(self) -> List[Dict[str, str]]:
        """Get workout URLs, explanations, and equipment for the user's query."""
        print(f"Processing request: {self.query}")
        
        # Step 1: Improve the YouTube search query
        prompt = self._build_query_prompt()
        improved_query = self._call_llm(prompt, max_tokens=50)
        print(f"Improved query: {improved_query}")

        if not improved_query:
            print("Using original query as fallback")
            improved_query = self.query

        # Step 2: Search YouTube
        results = self._search_youtube(improved_query, limit=4)  # Limit to 4 videos
        print(f"Found {len(results)} YouTube videos")

        # Step 3: Explain each video
        recommendations = []
        for i, video in enumerate(results, 1):
            print(f"Processing video {i}/{len(results)}")
            video_id = video["id"]
            title = video["title"]
            description = video.get("descriptionSnippet", [{'text': ''}])[0]['text']
            transcript = self._get_transcript(video_id)

            explanation_prompt = self._build_explanation_prompt(title, description, transcript)
            llm_response = self._call_llm(explanation_prompt, max_tokens=200)
            print(f"Generated explanation for: {title}")

            # Parse the LLM response to get explanation and equipment
            parsed_response = self._parse_llm_response(llm_response)

            recommendations.append({
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "explanation": parsed_response["explanation"],
                "equipment": parsed_response["equipment"]
            })

        return recommendations 