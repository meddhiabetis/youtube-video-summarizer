import sys
import os

# Add the src folder to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.youtube_fetcher import download_video_audio, get_video_metadata

# Example: Replace this with any YouTube video link
youtube_url = "https://www.youtube.com/watch?v=zxQyTK8quyY"

# Fetch metadata
metadata = get_video_metadata(youtube_url)
if metadata:
    print("Video Metadata:")
    for key, value in metadata.items():
        print(f"{key}: {value}")

# Download audio
audio_path = download_video_audio(youtube_url)
if audio_path:
    print(f"Audio saved at: {audio_path}")