import sys
import os
import json

# Add the src folder to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.transcription import transcribe_audio

def test_transcription():
    # Path configuration
    audio_filename = "Transformer Neural Networks, ChatGPT's foundation, Clearly Explained!!!.m4a"
    audio_path = os.path.join("downloads", audio_filename)
    
    # Output files
    transcription_json_path = os.path.join("downloads", "transcription.json")
    transcription_text_path = os.path.join("downloads", "transcription.txt")

    # Verify file exists
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        print("Available files in downloads:")
        for f in os.listdir("downloads"):
            print(f" - {f}")
        return

    # Transcribe with enhanced function
    print(f"\nStarting enhanced transcription of {audio_filename}...")
    result = transcribe_audio(
        audio_path,
        model_size="small",  # Recommended balance of speed/accuracy
        timestamp_resolution="word"
    )

    if result and result.get("segments"):
        # Save full JSON output
        with open(transcription_json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nFull JSON transcription saved to {transcription_json_path}")

        # Save human-readable version
        with open(transcription_text_path, "w", encoding="utf-8") as f:
            f.write(f"Language: {result.get('language', 'unknown')}\n\n")
            for segment in result["segments"]:
                f.write(f"[{segment['start']:.1f}-{segment['end']:.1f}s]: {segment['text']}\n")
                if "words" in segment:
                    for word in segment["words"]:
                        f.write(f"  {word['start']:.2f}s: {word['word']}\n")
                f.write("\n")
        
        print(f"Readable transcription saved to {transcription_text_path}")
        print(f"\nSample output:")
        print(f"Detected language: {result.get('language')}")
        print(f"First segment: {result['segments'][0]['text'][:100]}...")
        print(f"Total segments: {len(result['segments'])}")

    else:
        print("Transcription failed. Error:", result.get("error", "Unknown error"))

if __name__ == "__main__":
    test_transcription()