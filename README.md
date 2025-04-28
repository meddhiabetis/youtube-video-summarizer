# 🎥 YouTube Video Summarizer

[![Repo Link](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/meddhiabetis/youtube-video-summarizer)

## Overview
**YouTube Video Summarizer** is an intelligent tool designed to automatically transcribe, summarize, and assist with educational YouTube video content, making complex information more accessible for students and lifelong learners.

It leverages **OpenAI Whisper** for accurate transcription, integrates advanced **Language Models** for generating clear and concise summaries, and features an interactive **Assistant** to help users engage more deeply with the content — all accessible through a simple, intuitive **Streamlit** web interface.

---

## ✨ Features
- 📥 Fetch YouTube videos and extract audio.
- 📝 Transcribe audio using state-of-the-art Whisper models.
- ✂️ Generate smart, educational summaries.
- 🌐 Easy-to-use web interface powered by Streamlit.
- 🔒 Environment variable support for API keys.

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/meddhiabetis/youtube-video-summarizer.git
cd youtube-video-summarizer
```

### 2. Install Python Dependencies
It’s recommended to use a virtual environment (.venv):

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install FFmpeg
Whisper requires FFmpeg. Install it via:

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg
```

On macOS (with Homebrew):

```bash
brew install ffmpeg
```

On Windows:

Download from FFmpeg.org and add it to your PATH.

Note: Verify installation by running `ffmpeg -version`.

### 4. Create a .env file
Inside the project root, create a .env file and add your API key:

```
GROQ_API_KEY=your_key_here
```

### 5. Run the App
```bash
streamlit run src/app.py
```

📂 Project Structure
```
youtube-video-summarizer/
├── src/
│   ├── app.py                # Main Streamlit app
│   ├── assistant.py           # Video assistant and LLM interface
│   ├── transcription.py       # Handles transcription using Whisper
│   ├── summarization.py       # Summarization logic (LLM integration)
│   └── youtube_fetcher.py     # Fetch YouTube video/audio
├── tests/
│   ├── test_transcription.py  # Unit tests for transcription
│   ├── test_summarization.py  # Unit tests for summarization
│   └── test_youtube_fetcher.py# Unit tests for YouTube fetcher
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore file
├── README.md                  # Project documentation
└── .env                       # API keys and environment variables
```


