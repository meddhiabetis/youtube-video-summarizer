import os
import json
import streamlit as st
from datetime import timedelta
from youtube_fetcher import download_video_audio, get_video_metadata
from transcription import transcribe_audio
from summarization import YouTubeSummarizer
from assistant import VideoAssistant

# Configure page
st.set_page_config(
    page_title="YouTube AI Assistant",
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
    .chat-message-user {
        background-color: #e3f2fd;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .chat-message-assistant {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .timestamp-link {
        color: #1e88e5;
        font-weight: bold;
        text-decoration: none;
    }
    .stProgress > div > div > div > div {
        background-color: #1e88e5;
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
               f"Sections: {len(summary['sections'])}")
    
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
                clean_summary = "\n".join(
                    line for line in section['summary'].split('\n')
                    if not line.lower().startswith("here is the summary")
                )
                st.markdown(clean_summary)
        
        st.divider()

def chat_interface(assistant: VideoAssistant):
    """Display chat interface"""
    st.subheader("💬 Video Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask anything about the video..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.spinner("Thinking..."):
            response = assistant.generate_response(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

def extract_video_id(url: str) -> str:
    """Extract video ID from URL"""
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return url

def main():
    st.title("🎥 YouTube AI Assistant")
    st.markdown("""
    Complete YouTube video processing pipeline:
    1. Download video audio
    2. Generate transcript with timestamps
    3. Create AI-powered summary
    4. Interactive Q&A about the video
    """)
    
    # Initialize session state
    if "processing_stage" not in st.session_state:
        st.session_state.processing_stage = None
    if "summary" not in st.session_state:
        st.session_state.summary = None
    if "assistant" not in st.session_state:
        st.session_state.assistant = VideoAssistant()
    
    # Input section
    with st.form("youtube_form"):
        youtube_url = st.text_input("YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
        use_groq = st.checkbox("Use enhanced AI summaries (requires Groq API key)", 
                             value=True,
                             help="Uses Groq's AI for higher quality summaries if available")
        submitted = st.form_submit_button("Process Video")
    
    if submitted and youtube_url:
        try:
            video_id = extract_video_id(youtube_url)
            
            # Processing pipeline
            with st.status("Processing video...", expanded=True) as status:
                # Step 1: Fetch metadata
                st.write("🔍 Fetching video metadata...")
                metadata = get_video_metadata(youtube_url)
                
                if not metadata:
                    st.error("Couldn't fetch video metadata")
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
                st.write("⬇️ Downloading audio...")
                audio_path = download_video_audio(youtube_url)
                if not audio_path:
                    st.error("Failed to download audio")
                    return
                
                # Step 3: Transcribe
                st.write("🎤 Transcribing audio...")
                transcription = transcribe_audio(
                    audio_path,
                    model_size="small",
                    timestamp_resolution="word"
                )
                
                if "error" in transcription:
                    st.error(f"Transcription failed: {transcription['error']}")
                    return
                
                # Step 4: Summarize
                st.write("🧠 Generating summary...")
                summarizer = YouTubeSummarizer()
                summary = summarizer.generate_summary(transcription)
                summary['metadata']['video_id'] = video_id
                
                # Save summary
                os.makedirs("downloads", exist_ok=True)
                with open("downloads/latest_summary.json", "w") as f:
                    json.dump(summary, f)
                
                # Update session state
                st.session_state.summary = summary
                st.session_state.assistant.load_summary()
                
                status.update(label="Processing complete!", state="complete", expanded=False)
            
            # Display results
            st.success("✅ Video processed successfully!")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()
    
    # Display summary if available
    if st.session_state.summary:
        display_summary(
            st.session_state.summary,
            st.session_state.summary['metadata']['video_id']
        )
        chat_interface(st.session_state.assistant)

if __name__ == "__main__":
    main()