# YouTube Video Summarizer

## Overview
This project summarizes educational YouTube videos to provide concise, accessible information for students. It transcribes video audio using Whisper and generates summaries using advanced language models.

## Features
- Fetch YouTube videos and transcribe audio.
- Generate text-based summaries tailored for educational content.
- Streamlit-based web interface for ease of use.

## Tech Stack
- **Python**: Core programming language.
- **Streamlit**: For the web interface.
- **Whisper**: For transcription.
- **LLMs**: To generate summaries.

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd youtube-summarizer
   ```
2. Run the setup script:
   ```bash
   ./setup.sh
   ```
3. Start the app:
   ```bash
   streamlit run src/app.py
   ```

## Project Structure
```
youtube-summarizer/
├── src/
│   ├── app.py                # Main Streamlit app
│   ├── transcription.py      # Handles transcription using Whisper
│   ├── summarization.py      # Summarization logic (LLM integration)
│   ├── youtube_fetcher.py    # Fetch YouTube video/audio
│   └── utils.py              # Helper functions
├── tests/
│   ├── test_transcription.py # Unit tests for transcription
│   ├── test_summarization.py # Unit tests for summarization
│   └── test_youtube_fetcher.py # Unit tests for YouTube fetcher
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore file
├── README.md                 # Project documentation
└── setup.sh                  # Script to set up the environment
```

## Roadmap
- [x] Set up project structure and environment.
- [ ] Implement transcription with Whisper.
- [ ] Integrate summarization using LLMs.
- [ ] Build and deploy the Streamlit app.

## Contributing
Feel free to open issues or submit pull requests for improvements!