import os
from typing import Dict, List, Optional
from openai import OpenAI
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

class YouTubeSummarizer:
    def __init__(self):
        # Initialize Groq client if API key exists
        self.groq_client = None
        if GROQ_API_KEY:
            try:
                self.groq_client = OpenAI(
                    api_key=GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )
            except Exception as e:
                print(f"Failed to initialize Groq client: {str(e)}")

    def _generate_groq_summary(self, text: str) -> Optional[str]:
        """Generate enhanced summary using Groq API"""
        if not self.groq_client:
            return None
            
        system_prompt = """You are an expert technical content summarizer. Create a comprehensive summary with:
        - Original timestamps preserved in [HH:MM:SS] format
        - Clear section titles reflecting content
        - Bullet points for important details
        - No introductory phrases"""
        
        user_prompt = f"""Please summarize this technical content:

        {text}

        Required format:
        [HH:MM:SS] Specific Section Title
        - Key concept 1
        - Key concept 2
        - Technical detail
        - Practical application

        Do not include any introductory text like "Here is the summary"."""

        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {str(e)}")
            return None

    def _create_sections(self, segments: List[Dict], min_duration: int = 60, max_duration: int = 300) -> List[Dict]:
        """Create time-based sections with balanced durations"""
        if not segments:
            return []
        
        sections = []
        current_section = []
        
        for seg in segments:
            if not current_section:
                current_section.append(seg)
            else:
                section_duration = seg['end'] - current_section[0]['start']
                if section_duration < max_duration:
                    current_section.append(seg)
                else:
                    if (current_section[-1]['end'] - current_section[0]['start']) >= min_duration:
                        sections.append({
                            'start': current_section[0]['start'],
                            'end': current_section[-1]['end'],
                            'segments': current_section
                        })
                    current_section = [seg]
        
        if current_section and (current_section[-1]['end'] - current_section[0]['start']) >= min_duration:
            sections.append({
                'start': current_section[0]['start'],
                'end': current_section[-1]['end'],
                'segments': current_section
            })
        
        return sections

    def _extract_section_title(self, summary: str) -> str:
        """Extract the first line as section title"""
        if not summary:
            return "Section"
        first_line = summary.split('\n')[0]
        if ']' in first_line:
            return first_line.split(']')[-1].strip()
        return first_line.strip()

    def generate_section_summary(self, section: Dict, use_groq: bool = True) -> Dict:
        """Generate summary for one section with proper formatting"""
        full_text = " ".join(seg['text'] for seg in section['segments'])
        timestamp = self.format_timestamp(section['start'])
        
        if use_groq and self.groq_client:
            groq_summary = self._generate_groq_summary(f"[{timestamp}] {full_text}")
            if groq_summary:
                return {
                    'start': section['start'],
                    'end': section['end'],
                    'summary': groq_summary,
                    'title': self._extract_section_title(groq_summary)
                }
        
        # Fallback format
        return {
            'start': section['start'],
            'end': section['end'],
            'summary': f"[{timestamp}] {full_text[:200]}{'...' if len(full_text) > 200 else ''}",
            'title': "Section"
        }

    def generate_full_summary(self, transcription: Dict, use_groq: bool = True) -> Dict:
        """Generate complete summary for all sections"""
        sections = self._create_sections(transcription['segments'])
        section_summaries = []
        
        for i, section in enumerate(sections, 1):
            try:
                print(f"Processing section {i}/{len(sections)}...")
                section_summaries.append(self.generate_section_summary(section, use_groq))
            except Exception as e:
                print(f"Skipping section {i} due to error: {str(e)}")
                continue
        
        return {
            'metadata': {
                'language': transcription.get('language', 'en'),
                'duration': transcription['segments'][-1]['end'],
                'total_sections': len(section_summaries),
                'groq_used': use_groq and bool(self.groq_client)
            },
            'sections': section_summaries
        }

    def format_timestamp(self, seconds: float) -> str:
        """Format seconds into HH:MM:SS"""
        return str(timedelta(seconds=int(seconds))).split(".")[0]