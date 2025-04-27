from pytubefix import YouTube
import os


def download_video_audio(youtube_url, output_path="downloads"):
    try:
        os.makedirs(output_path, exist_ok=True)
        print(f"Trying to fetch video from URL: {youtube_url}")
        yt = YouTube(youtube_url)  # This might throw an error

        print(f"Video title: {yt.title}")
        print(f"Available streams: {yt.streams}")
        
        # Get the audio stream with the highest quality
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            print("No audio stream found!")
            return None

        audio_file_path = audio_stream.download(output_path)
        print(f"Audio downloaded successfully to: {audio_file_path}")
        return audio_file_path

    except Exception as e:
        print(f"Error downloading video audio: {e}")
        return None

def get_video_metadata(youtube_url):
    try:
        print(f"Trying to fetch metadata from URL: {youtube_url}")
        yt = YouTube(youtube_url)  # This might throw an error

        metadata = {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,  # Duration in seconds
            "views": yt.views,
            "description": yt.description,
            "publish_date": yt.publish_date,
        }
        return metadata

    except Exception as e:
        print(f"Error fetching video metadata: {e}")
        return None