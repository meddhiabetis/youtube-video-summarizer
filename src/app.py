import os
import json
import streamlit as st
from youtube_fetcher import download_video_audio, get_video_metadata
from transcription import transcribe_audio
from summarization import YouTubeSummarizer
from datetime import timedelta

# Configure page
st.set_page_config(
    page_title="YouTube Summarizer",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .summary-section {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .highlight {
        background-color: #fffacd;
        padding: 2px 5px;
        border-radius: 3px;
    }
    .timestamp-link {
        color: #1e88e5;
        font-weight: bold;
        text-decoration: none;
    }
    .timestamp-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format"""
    return str(timedelta(seconds=int(seconds))).split(".")[0]

def create_youtube_timestamp_link(video_id: str, seconds: int) -> str:
    """Create YouTube link with timestamp"""
    return f"https://youtu.be/{video_id}?t={int(seconds)}"

def display_summary(summary: dict, video_id: str):
    """Render summary in Streamlit with formatted sections"""
    st.subheader("📝 Video Summary")
    st.caption(f"Duration: {format_timestamp(summary['metadata']['duration'])} | "
               f"Sections: {summary['metadata']['total_sections']}")
    
    for section in summary['sections']:
        with st.container():
            # Create clickable timestamp
            timestamp_link = create_youtube_timestamp_link(
                video_id,
                section['start']
            )
            
            st.markdown(f"""
            ### <a href="{timestamp_link}" class="timestamp-link" target="_blank">
            🕒 {format_timestamp(section['start'])} - {section.get('title', 'Section')}
            </a>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 4])
            with col1:
                st.metric("Duration", format_timestamp(section['end'] - section['start']))
            
            with col2:
                # Remove any "Here is the summary" lines
                clean_summary = "\n".join(
                    line for line in section['summary'].split('\n')
                    if not line.lower().startswith("here is the summary")
                )
                st.markdown(clean_summary)
        
        st.divider()

def extract_video_id(url: str) -> str:
    """Extract video ID from URL"""
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return url

def main():
    st.title("🎥 YouTube Video Summarizer")
    st.markdown("""
    Paste a YouTube URL below to get:
    - Full transcript with timestamps
    - AI-generated summary
    - Key technical concepts
    """)
    
    # Input section
    with st.form("youtube_form"):
        youtube_url = st.text_input("YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
        use_groq = st.checkbox("Use enhanced AI summaries (requires Groq API key)", 
                             value=True,
                             help="Uses Groq's AI for higher quality summaries if API key is available")
        submitted = st.form_submit_button("Summarize Video")
    
    if submitted and youtube_url:
        with st.spinner("Processing video..."):
            try:
                video_id = extract_video_id(youtube_url)
                
                # Step 1: Fetch video metadata
                st.info("🔍 Fetching video metadata...")
                metadata = get_video_metadata(youtube_url)
                
                if not metadata:
                    st.error("Couldn't fetch video metadata. Please check the URL.")
                    return
                
                # Display video info
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", 
                            caption="Video thumbnail")
                with col2:
                    st.subheader(metadata['title'])
                    st.caption(f"👤 {metadata['author']} | ⏱️ {format_timestamp(metadata['length'])} | "
                              f"👀 {metadata['views']:,} views")
                
                # Step 2: Download audio
                st.info("⬇️ Downloading audio...")
                audio_path = download_video_audio(youtube_url)
                if not audio_path:
                    st.error("Failed to download audio. Please try another video.")
                    return
                
                # Step 3: Transcribe
                st.info("🎤 Transcribing audio...")
                transcription = transcribe_audio(
                    audio_path,
                    model_size="small",  # Balanced speed/accuracy
                    timestamp_resolution="word"
                )
                
                if "error" in transcription:
                    st.error(f"Transcription failed: {transcription['error']}")
                    return
                
                # Step 4: Summarize
                st.info("🧠 Generating summary...")
                summarizer = YouTubeSummarizer()
                summary = summarizer.generate_full_summary(transcription, use_groq=use_groq)
                
                # Display results
                st.success("✅ Processing complete!")
                display_summary(summary, video_id)
                
                # Download buttons
                st.download_button(
                    label="Download Full Transcript (JSON)",
                    data=json.dumps(transcription, indent=2),
                    file_name="transcription.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.stop()

if __name__ == "__main__":
    main()