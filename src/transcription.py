import whisper
import os
from typing import List, Dict, Optional
import json
import torch

def transcribe_audio(
    audio_path: str,
    model_size: str = "base",
    language: Optional[str] = None,
    timestamp_resolution: str = "word"  # or "segment"
) -> Dict:
    """
    Enhanced audio transcription with timestamps using OpenAI Whisper.

    Args:
        audio_path: Path to the audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Language code (None for auto-detection)
        timestamp_resolution: Granularity of timestamps ("word" or "segment")

    Returns:
        Dictionary containing:
        {
            "text": full_text,
            "segments": [
                {
                    "text": segment_text,
                    "start": start_time,
                    "end": end_time,
                    "words": [  # only if word-level
                        {"word": str, "start": float, "end": float}
                    ]
                }
            ],
            "language": detected_language
        }
    """
    try:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"Checking CUDA availability...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        print(f"Loading Whisper {model_size} model on {device}...")
        model = whisper.load_model(model_size, device=device)

        # Configure transcription options
        transcribe_args = {
            "verbose": False,
            "task": "transcribe",
            "word_timestamps": timestamp_resolution == "word"
        }
        if language:
            transcribe_args["language"] = language

        print(f"Transcribing {audio_path}...")
        result = model.transcribe(audio_path, **transcribe_args)

        # Process output for consistent format
        output = {
            "text": result["text"],
            "language": result.get("language", "en"),  # default to English
            "segments": []
        }

        for segment in result["segments"]:
            segment_data = {
                "text": segment["text"].strip(),
                "start": segment["start"],
                "end": segment["end"]
            }
            
            if timestamp_resolution == "word" and "words" in segment:
                segment_data["words"] = [
                    {
                        "word": w["word"],
                        "start": w["start"],
                        "end": w["end"]
                    } for w in segment["words"] if not w["word"].startswith("[")
                ]
            
            output["segments"].append(segment_data)

        print(f"Successfully transcribed {len(output['segments'])} segments")
        return output

    except Exception as e:
        print(f"Transcription failed: {str(e)}")
        return {
            "text": "",
            "segments": [],
            "error": str(e)
        }
