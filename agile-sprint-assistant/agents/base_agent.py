"""
Base Agent - Foundation for all specialized agents
Now includes Slack notification support and rate limiting
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys
import time

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.slack_helper import SlackNotifier

load_dotenv()

class BaseAgent:
    def __init__(self):
        """Initialize base agent with Gemini AI and Slack"""
        # Configure Gemini AI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Use gemini-2.5-flash - best balance of speed, quality, and quota
        self.model = genai.GenerativeModel("models/gemini-2.5-flash")
        print(f"[AI] ✅ Using model: gemini-2.5-flash")
        
        # Conversation context
        self.context = []
        
        # Initialize Slack notifier
        self.slack = SlackNotifier()
        
        # Session tracking
        self.session_id = None
        self.current_sprint = None
    
    def add_context(self, role: str, content: str):
        """Add message to conversation context"""
        self.context.append({
            "role": role,
            "content": content
        })
    
    def clear_context(self):
        """Clear conversation history"""
        self.context = []
    
    def get_context_string(self):
        """Get formatted context for prompts"""
        context_str = ""
        for item in self.context:
            context_str += f"[{item['role']}]: {item['content']}\n\n"
        return context_str
    
    def generate_response(self, prompt: str) -> str:
        """Generate AI response using Gemini with retry logic"""
        max_retries = 3
        retry_delay = 30  # seconds
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a quota error
                if "quota" in error_msg.lower() or "rate limit" in error_msg.lower() or "429" in error_msg:
                    if attempt < max_retries - 1:
                        print(f"[API] ⚠️ Rate limit hit. Waiting {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        return f"""[ERROR] API rate limit exceeded. Please wait a minute and try again.

Current model: gemini-2.5-flash
Free tier limits: Multiple requests per minute allowed
Wait 60 seconds and try again."""
                else:
                    print(f"[AI Error] {error_msg}")
                    return f"Error generating response: {error_msg}"
        
        return "[ERROR] Failed to generate response after multiple retries."
    
    def extract_sprint_number(self, session_id: str) -> int:
        """Extract sprint number from session ID"""
        try:
            # Expected format: "AlphaTeam_Sprint_3"
            return int(session_id.split("_")[-1])
        except:
            return 0