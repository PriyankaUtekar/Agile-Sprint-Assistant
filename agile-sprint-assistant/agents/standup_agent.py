"""
Standup Agent - Manages daily standups
With completion tracking and enhanced logging
"""
import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from agents.base_agent import BaseAgent
from database.db_manager import DatabaseManager

class StandupAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.standup_started = False
        self.updates = []
        self.summary_generated = False
        print("[StandupAgent] Initialized with summary_generated=False")
    
    def start_standup(self, session_id: str):
        """Start a new standup session"""
        self.session_id = session_id
        self.current_sprint = self.extract_sprint_number(session_id)
        self.standup_started = True
        self.summary_generated = False  # Reset on new session
        self.clear_context()
        print(f"[StandupAgent] Started standup, summary_generated={self.summary_generated}")
        
        db = DatabaseManager()
        sprint = db.get_sprint(session_id)
        
        if not sprint:
            return f"[ERROR] Sprint '{session_id}' not found in database."
        
        message = f"""
[STANDUP STARTED]
Sprint: {self.current_sprint}
Date: {self.get_today_date()}

Daily standup has begun! Team members can now share their updates.
        """
        
        self.add_context("system", message)
        return message
    
    def collect_update(self, member: str, yesterday: str, today: str, blockers: str = "None"):
        """Collect a team member's standup update"""
        if not self.standup_started:
            return "[ERROR] Standup session not started"
        
        update = {
            "member": member,
            "yesterday": yesterday,
            "today": today,
            "blockers": blockers
        }
        
        self.updates.append(update)
        print(f"[StandupAgent] Collected update from {member}, total updates: {len(self.updates)}")
        
        result = f"""
[UPDATE RECORDED]
Member: {member}
Yesterday: {yesterday}
Today: {today}
Blockers: {blockers}

Update recorded successfully! ({len(self.updates)} updates collected)
        """
        
        self.add_context("update", result)
        return result
    
    def generate_summary(self):
        """Generate AI-powered standup summary"""
        print(f"[StandupAgent] generate_summary called, summary_generated={self.summary_generated}")
        
        if not self.standup_started:
            print("[StandupAgent] ERROR: Standup not started")
            return {"error": "Standup session not started"}
        
        if len(self.updates) == 0:
            print("[StandupAgent] ERROR: No updates to summarize")
            return {"error": "No updates to summarize"}
        
        # Format updates for AI
        updates_text = ""
        for update in self.updates:
            updates_text += f"\n{update['member']}:\n"
            updates_text += f"  Yesterday: {update['yesterday']}\n"
            updates_text += f"  Today: {update['today']}\n"
            updates_text += f"  Blockers: {update['blockers']}\n"
        
        prompt = f"""
You are an AI Scrum Master. Generate a concise daily standup summary.

Sprint {self.current_sprint}
Team Updates:
{updates_text}

Create a summary that includes:

1. KEY HIGHLIGHTS
   - Main accomplishments from yesterday
   - Focus areas for today

2. BLOCKERS & ISSUES
   - List all blockers mentioned
   - Categorize by severity
   - Suggest immediate actions

3. TEAM VELOCITY
   - Overall progress assessment
   - Any concerns or risks

4. ACTION ITEMS
   - Specific follow-ups needed
   - Who needs to do what

Be concise and actionable.
        """
        
        summary_text = self.generate_response(prompt)
        print("[StandupAgent] Summary generated successfully")
        
        # Extract blockers
        blockers = []
        for update in self.updates:
            if update['blockers'].lower() not in ['none', 'no blockers', 'nothing']:
                blockers.append(f"{update['member']}: {update['blockers']}")
        
        # Store in database
        try:
            db = DatabaseManager()
            sprint = db.get_sprint(self.session_id)
            if sprint:
                for update in self.updates:
                    db.store_standup(
                        sprint.id,
                        update['member'],
                        update['yesterday'],
                        update['today'],
                        update['blockers']
                    )
                print(f"[StandupAgent] Stored {len(self.updates)} updates in database")
        except Exception as e:
            print(f"[StandupAgent Error] Failed to store updates: {e}")
        
        # Send to Slack
        try:
            if self.slack.is_enabled():
                slack_sent = self.slack.send_standup_summary(
                    self.current_sprint,
                    summary_text[:500],  # Truncate for Slack
                    blockers
                )
                if slack_sent:
                    print(f"[StandupAgent] Summary sent to Slack!")
                    summary_text += "\n\n[Team has been notified on Slack!]"
        except Exception as e:
            print(f"[StandupAgent Error] Failed to send Slack: {e}")
        
        # CRITICAL: Mark summary as generated
        self.summary_generated = True
        print(f"[StandupAgent] MARKED COMPLETE: summary_generated={self.summary_generated}")
        
        return {
            "summary_text": summary_text,
            "blockers": blockers
        }
    
    def is_completed(self):
        """Check if standup is completed (summary generated)"""
        print(f"[StandupAgent] is_completed() called, returning: {self.summary_generated}")
        return self.summary_generated
    
    def get_today_date(self):
        """Get today's date"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")