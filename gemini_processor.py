from google import genai
from google.genai import types
import time
import json
import os
from typing import Optional
from config import GEMINI_API_KEY, logger, MeetingMinutes

class MeetingIntelligence:
    def __init__(self):
        # Explicitly pass the key from our config to override system env vars
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        # Using 2.5 Flash as your previous 'list_models' showed it's the current stable version
        self.model_id = "gemini-2.5-flash"
        self.system_instruction = (
            "You are an expert meeting analyst. You will be provided with an audio file of a meeting. "
            "Your task is to transcribe and analyze the meeting. "
            "Return a JSON object that strictly matches the following schema: "
            "{\n"
            "  \"title\": \"A concise meeting title\", \n"
            "  \"summary\": \"A short summary of the meeting\", \n"
            "  \"key_decisions\": [\"decision 1\", \"decision 2\"], \n"
            "  \"action_items\": [{\"task\": \"task description\", \"assignee\": \"person name\"}]\n"
            "}\n"
            "Provide ONLY the JSON output, no other text."
        )

    def process_audio(self, file_path: str) -> Optional[MeetingMinutes]:
        logger.info(f"Uploading audio file: {file_path}")
        
        try:
            # Upload file - The new SDK uses 'file' or 'path' depending on the version, 
            # but usually it's 'path' or 'file' for a path string.
            # In 1.0.0+, it's often client.files.upload(path=path)
            # Let's try the most compatible way for the current 1.65.0 version.
            audio_file = self.client.files.upload(file=file_path)
            
            # Wait for file to be ready
            while audio_file.state == "PROCESSING":
                logger.info("Waiting for audio processing...")
                time.sleep(5)
                audio_file = self.client.files.get(name=audio_file.name)

            if audio_file.state == "FAILED":
                logger.error("Audio processing failed on Gemini server.")
                return None

            logger.info("Generating meeting minutes...")
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    audio_file,
                    "Analyze this meeting audio and provide the structured minutes."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    response_mime_type="application/json"
                )
            )
            
            # Immediate cleanup from Google Cloud
            self.client.files.delete(name=audio_file.name)
            logger.info("Deleted audio file from Gemini servers.")

            try:
                # The new SDK might return a dict or a string depending on response_mime_type
                # Usually it's in response.text
                text = response.text.strip()
                data = json.loads(text)
                return MeetingMinutes(**data)
            except Exception as e:
                logger.error(f"Failed to parse Gemini response: {e}")
                logger.debug(f"Raw response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Gemini processing error: {e}")
            return None
