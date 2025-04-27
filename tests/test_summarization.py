import os
import sys
import json
from pprint import pprint
from time import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.summarization import YouTubeSummarizer


def test_summarization():
    # Config
    trans_path = "downloads/transcription.json"
    out_json = "downloads/summary.json"
    out_txt = "downloads/summary.txt"

    print("Initializing summarizer...")
    summarizer = YouTubeSummarizer()
    groq_available = (
        hasattr(summarizer, "groq_client") and summarizer.groq_client is not None
    )

    try:
        print("Loading transcription...")
        with open(trans_path, "r", encoding="utf-8") as f:
            transcription = json.load(f)

        total_segments = len(transcription["segments"])
        print(f"Loaded {total_segments} segments")
        print(
            f"Total duration: {summarizer.format_timestamp(transcription['segments'][-1]['end'])}"
        )

        # Test both modes if Groq is available
        test_modes = [True, False] if groq_available else [False]

        for use_groq in test_modes:
            print(f"\n{'='*40}")
            print(f"Testing with Groq: {'ON' if use_groq else 'OFF'}")
            print(f"{'='*40}")

            start_time = time()
            summary = summarizer.generate_full_summary(transcription, use_groq=use_groq)
            elapsed = time() - start_time

            print(
                f"\nGenerated {len(summary['sections'])} sections in {elapsed:.1f} seconds"
            )

            if use_groq and groq_available:
                groq_success = summary["metadata"]["groq_success"]
                total = summary["metadata"]["total_sections"]
                print(f"Groq success rate: {groq_success}/{total} sections")

            # Save results with mode-specific filenames
            mode = "groq" if use_groq else "simple"
            json_path = f"downloads/summary_{mode}.json"
            txt_path = f"downloads/summary_{mode}.txt"

            summarizer.save_summary(summary, json_path, txt_path)
            print(f"Saved results to {json_path} and {txt_path}")

            # Display sample output
            if summary["sections"]:
                print("\nSample Output Sections:")
                for i, section in enumerate(summary["sections"][:3], 1):
                    print(f"\nSection {i} ({section['source'].upper()}):")
                    print(f"[{summarizer.format_timestamp(section['start'])}]")
                    print(
                        section["summary"][:300]
                        + ("..." if len(section["summary"]) > 300 else "")
                    )

        print("\nTest completed successfully!")

    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        if "transcription" in locals():
            print("\nFirst segment:")
            pprint(transcription["segments"][0])
            print("\nLast segment:")
            pprint(transcription["segments"][-1])


if __name__ == "__main__":
    test_summarization()
