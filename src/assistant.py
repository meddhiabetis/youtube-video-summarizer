import json
import os
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import timedelta

load_dotenv()

class VideoAssistant:
    def __init__(self, top_k=3):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.groq_client = OpenAI(
            api_key=os.getenv('GROQ_API_KEY'),
            base_url="https://api.groq.com/openai/v1"
        ) if os.getenv('GROQ_API_KEY') else None
        self.summary = None
        self.section_embeddings = None
        self.summary_path = "downloads/latest_summary.json"
        self.conversation_history = []
        self.top_k = top_k
        
    def load_summary(self):
        """Load the latest summary and prepare embeddings"""
        if not os.path.exists(self.summary_path):
            raise FileNotFoundError("No summary file found")
        
        with open(self.summary_path, 'r') as f:
            self.summary = json.load(f)
        
        self._prepare_embeddings()
    
    def _prepare_embeddings(self):
        """Prepare embeddings for each section"""
        sections = [
            {
                'text': f"{section.get('title', '')}\n{section['summary']}",
                'start': section['start'],
                'end': section['end']
            }
            for section in self.summary['sections']
        ]
        
        texts = [s['text'] for s in sections]
        self.section_embeddings = {
            'texts': texts,
            'embeddings': self.model.encode(texts, normalize_embeddings=True),
            'sections': sections
        }
    
    def _find_relevant_sections(self, query: str) -> List[Dict]:
        """Find top_k most relevant sections using cosine similarity"""
        if not self.section_embeddings:
            self.load_summary()
        
        query_embedding = self.model.encode(query, normalize_embeddings=True)
        similarities = np.dot(self.section_embeddings['embeddings'], query_embedding)
        top_indices = np.argsort(similarities)[-self.top_k:][::-1]
        
        return [self.section_embeddings['sections'][i] for i in top_indices]
    
    def _build_context(self, sections: List[Dict]) -> str:
        return "\n\n".join(
            f"[From {format_timestamp(s['start'])} to {format_timestamp(s['end'])}]: {s['text']}"
            for s in sections
        )
    
    def generate_response(self, query: str) -> str:
        """Generate response using RAG + conversation history"""
        try:
            relevant_sections = self._find_relevant_sections(query)
            context = self._build_context(relevant_sections)

            self.conversation_history.append({"role": "user", "content": query})
            
            system_prompt = (
                "You are a highly knowledgeable AI assistant helping users understand a YouTube video."
                " Use the provided sections and conversation history to answer clearly, cite timestamps if useful."
                " If you don't have enough info, say you don't know."
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.conversation_history[-6:])  # Keep conversation history
            messages.append({
                "role": "user",
                "content": f"Video Context:\n{context}\n\nAnswer based on the context: {query}"
            })

            if not self.groq_client:
                return "No Groq API Key found."

            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                temperature=0.2,
                max_tokens=1200
            )
            assistant_reply = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_reply})
            return assistant_reply

        except Exception as e:
            return f"Error generating response: {str(e)}"

def format_timestamp(seconds: float) -> str:
    """Format seconds into HH:MM:SS"""
    return str(timedelta(seconds=int(seconds))).split(".")[0]
