"""This script defines the Fair Hire AI Service, a FastAPI-based application that processes audio interview transcripts 
to evaluate fairness and bias. The service exposes two main endpoints: one for transcribing audio files from a URL 
and another for scoring the transcription for fairness.
"""
import argparse
import logging
import os
import tempfile
from io import BytesIO
from typing import List, Tuple

import httpx
import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .ai_utils import score_transcript

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("fair-hire-ai-service")
logger.info("Initialization done! Agent is ready!")

openai_api_key =  os.environ["OPENAI_API_KEY"]

headers = {
    "Authorization": f"Bearer {openai_api_key}"
}

class AudioURLRequest(BaseModel):
    """Defines the request model for receiving audio file URL and position title 
        in the API request payload.
    """
    audio_url: str
    interview_position: str


@app.post("/transcribe_audio")
async def transcribe_audio(request: AudioURLRequest):
    """Receives an audio file URL, downloads the audio, and transcribes it to text 
        using the OpenAI API.

    Args:
        request: the API request payload

    Returns:
        The transcription as json
    """
    try:
        # Fetch audio file from the provided URL
        audio_response = requests.get(request.audio_url)
        audio_response.raise_for_status()  # Ensure the request was successful
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching audio file: {e}")

    # Load audio content into a BytesIO object
    audio_data =  BytesIO(audio_response.content)
    
    # Set up files for OpenAI API request
    files = {
        'file': ('audio.wav', audio_data, 'audio/wav'),
        'model': (None, 'whisper-1')
    }
    
    try:
        # Send audio data to OpenAI API for transcription
        response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files)
        response.raise_for_status()  # Check for request errors
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error with transcription service: {e}")

    # Extract transcription text from the response
    json_response = response.json()
    transcription_text = json_response.get("text", "")

    # Return the transcription text
    return {"transcription": transcription_text}


@app.post("/score")
async def score(request: AudioURLRequest):
    """For scoring the transcription for fairness.

    Args:
        request: the API request payload

    Returns:
        The score and explaination as json
    """

    try:
        # Call the transcribe_audio endpoint
        logging.info(request.audio_url)
        logging.info(request.interview_position)
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/transcribe_audio", json={"audio_url": request.audio_url,  "interview_position": request.interview_position})

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Transcription service failed.")

        transcription_result = response.json()
        ai_response = score_transcript(transcription_result["transcription"], request.interview_position)
        return {"ai_response": ai_response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start() -> None:
    """The start/entrypoint of service ."""
    parser = argparse.ArgumentParser(description="Fair Hire AI Service")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Webservice Host (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Webservice port (default: 8000)",
    )
    args = parser.parse_args()

    uvicorn.run(
        "fair_hire_ai.app:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )