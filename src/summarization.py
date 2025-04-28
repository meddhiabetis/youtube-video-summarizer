import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

class YouTubeSummarizer:
    def __init__(self):
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
        if not self.groq_client:
            return None
            
        system_prompt = """You are an expert technical content summarizer. Create a summary with:
        - Original timestamps preserved
        - Clear section titles
        - Bullet points for key concepts"""
        
        user_prompt = f"""Summarize this content:

        {text}

        Format:
        [HH:MM:SS] Specific Title
        - Key point 1
        - Key point 2"""

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

    def _create_sections(self, segments: List[Dict]) -> List[Dict]:
        if not segments:
            return []
        
        sections = []
        current_section = []
        
        for seg in segments:
            if not current_section:
                current_section.append(seg)
            else:
                section_duration = seg['end'] - current_section[0]['start']
                if section_duration < 180:  # 3 minute sections
                    current_section.append(seg)
                else:
                    sections.append({
                        'start': current_section[0]['start'],
                        'end': current_section[-1]['end'],
                        'segments': current_section
                    })
                    current_section = [seg]
        
        if current_section:
            sections.append({
                'start': current_section[0]['start'],
                'end': current_section[-1]['end'],
                'segments': current_section
            })
        
        return sections

    def generate_summary(self, transcription: Dict) -> Dict:
        sections = self._create_sections(transcription['segments'])
        section_summaries = []
        
        for section in sections:
            full_text = " ".join(seg['text'] for seg in section['segments'])
            timestamp = self.format_timestamp(section['start'])
            
            if self.groq_client:
                groq_summary = self._generate_groq_summary(f"[{timestamp}] {full_text}")
                if groq_summary:
                    section_summaries.append({
                        'start': section['start'],
                        'end': section['end'],
                        'summary': groq_summary
                    })
                    continue
            
            section_summaries.append({
                'start': section['start'],
                'end': section['end'],
                'summary': f"[{timestamp}] {full_text[:200]}{'...' if len(full_text) > 200 else ''}"
            })
        
        return {
            'metadata': {
                'language': transcription.get('language', 'en'),
                'duration': transcription['segments'][-1]['end'],
                'section_count': len(section_summaries)
            },
            'sections': section_summaries
        }

    def format_timestamp(self, seconds: float) -> str:
        return str(timedelta(seconds=int(seconds))).split(".")[0]