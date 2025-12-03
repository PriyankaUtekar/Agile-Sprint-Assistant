"""
Retrospective Agent - Manages sprint retrospectives
With completion tracking for reset protection
"""
import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from agents.base_agent import BaseAgent
from database.db_manager import DatabaseManager

class RetrospectiveAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.retro_started = False
        self.feedback = {
            "went_well": [],
            "not_well": [],
            "improve": []
        }
        self.team_sentiment = 7
        self.action_items_draft = []
        self.retrospective_id = None
        self.summary_generated = False  # NEW: Track if summary is generated
    
    def start_retrospective(self, session_id: str, facilitator: str):
        """Start a new retrospective session"""
        self.session_id = session_id
        self.current_sprint = self.extract_sprint_number(session_id)
        self.facilitator = facilitator
        self.retro_started = True
        self.summary_generated = False  # Reset on new session
        self.clear_context()
        self.feedback = {
            "went_well": [],
            "not_well": [],
            "improve": []
        }
        self.team_sentiment = 7
        self.action_items_draft = []
        
        # Get sprint info
        db = DatabaseManager()
        sprint = db.get_sprint(session_id)
        
        if not sprint:
            return f"[ERROR] Sprint '{session_id}' not found in database."
        
        message = f"""
[RETROSPECTIVE STARTED]
Sprint: {self.current_sprint}
Facilitator: {facilitator}
Status: {sprint.status}

Sprint retrospective has begun! Time to reflect on what happened during the sprint.

STEP 1: Team members share feedback in three categories:
   - What went well
   - What didn't go well
   - What can we improve

STEP 2: Set team sentiment (1-10)

STEP 3: Create action items based on feedback

STEP 4: Generate comprehensive summary (including action items)
        """
        
        self.add_context("system", message)
        return message
    
    def add_feedback(self, category: str, feedback_text: str, submitted_by: str):
        """Add feedback to a category"""
        if not self.retro_started:
            return "[ERROR] Retrospective session not started"
        
        feedback_item = {
            "text": feedback_text,
            "submitted_by": submitted_by
        }
        
        if category in self.feedback:
            self.feedback[category].append(feedback_item)
            
            category_display = {
                "went_well": "What Went Well",
                "not_well": "What Didn't Go Well",
                "improve": "What Can We Improve"
            }
            
            result = f"""
[FEEDBACK ADDED]
Category: {category_display.get(category, category)}
Submitted by: {submitted_by}
Feedback: {feedback_text}

Feedback recorded successfully!
            """
            
            self.add_context("feedback", result)
            return result
        else:
            return "[ERROR] Invalid category. Use: went_well, not_well, or improve"
    
    def set_team_sentiment(self, sentiment: int):
        """Set team sentiment score (1-10)"""
        if not self.retro_started:
            return "[ERROR] Retrospective session not started"
        
        if sentiment < 1 or sentiment > 10:
            return "[ERROR] Team sentiment must be between 1 and 10"
        
        self.team_sentiment = sentiment
        
        sentiment_label = "Very Positive" if sentiment >= 8 else "Positive" if sentiment >= 6 else "Neutral" if sentiment >= 4 else "Needs Attention"
        
        result = f"""
[TEAM SENTIMENT SET]
Score: {sentiment}/10
Mood: {sentiment_label}

Team sentiment has been recorded. Ready to create action items.
        """
        
        self.add_context("sentiment", result)
        return result
    
    def create_action_items(self, items: list):
        """
        Create action items draft (not stored in DB yet)
        """
        if not self.retro_started:
            return "[ERROR] Retrospective session not started"
        
        self.action_items_draft = []
        
        for idx, item in enumerate(items, 1):
            action_item = {
                "number": idx,
                "title": item["title"],
                "description": item.get("description", ""),
                "assigned_to": item["assigned_to"],
                "priority": item["priority"],
                "target_date": item.get("target_date")
            }
            self.action_items_draft.append(action_item)
        
        result = f"""
[ACTION ITEMS DRAFTED]
Created {len(self.action_items_draft)} action items for Sprint {self.current_sprint}:

"""
        for item in self.action_items_draft:
            result += f"""
- Item {item['number']}: {item['title']}
  Assigned: {item['assigned_to']} | Priority: {item['priority']}
"""
        
        result += "\nAction items are ready. Now generate the retrospective summary to finalize everything."
        
        self.add_context("actions_draft", result)
        return result
    
    def generate_summary(self):
        """Generate comprehensive retrospective summary and store everything"""
        if not self.retro_started:
            return {"error": "Retrospective session not started"}
        
        db = DatabaseManager()
        sprint = db.get_sprint(self.session_id)
        
        if not sprint:
            return {"error": "Sprint not found"}
        
        # Format feedback for AI
        went_well_text = "\n".join([f"- {item['text']} (by {item['submitted_by']})" 
                                    for item in self.feedback["went_well"]])
        not_well_text = "\n".join([f"- {item['text']} (by {item['submitted_by']})" 
                                   for item in self.feedback["not_well"]])
        improve_text = "\n".join([f"- {item['text']} (by {item['submitted_by']})" 
                                  for item in self.feedback["improve"]])
        
        # Format action items for AI context
        action_items_text = ""
        if self.action_items_draft:
            action_items_text = "\n".join([
                f"- {item['title']} (Assigned: {item['assigned_to']}, Priority: {item['priority']})"
                for item in self.action_items_draft
            ])
        else:
            action_items_text = "No action items created"
        
        prompt = f"""
You are an AI Scrum Master facilitating a sprint retrospective. Generate a comprehensive summary.

Sprint {self.current_sprint}
Team Sentiment: {self.team_sentiment}/10
Facilitator: {self.facilitator}

WHAT WENT WELL:
{went_well_text if went_well_text else "No feedback provided"}

WHAT DIDN'T GO WELL:
{not_well_text if not_well_text else "No feedback provided"}

WHAT CAN WE IMPROVE:
{improve_text if improve_text else "No feedback provided"}

ACTION ITEMS CREATED:
{action_items_text}

Create a comprehensive summary with: Executive Summary, Detailed Analysis, Patterns, Action Items Review, Key Takeaways, and Recommendations.
        """
        
        summary_text = self.generate_response(prompt)
        
        # Store in database
        try:
            retro_id = db.store_retrospective(
                self.session_id,
                self.facilitator,
                self.feedback["went_well"],
                self.feedback["not_well"],
                self.feedback["improve"],
                summary_text,
                self.team_sentiment
            )
            self.retrospective_id = retro_id
            print(f"[Retrospective] Summary stored with ID: {retro_id}")
            
            # Store action items
            if self.action_items_draft:
                for item in self.action_items_draft:
                    action_id = f"AI-{self.current_sprint:03d}-{item['number']:02d}"
                    db.store_action_item(
                        retro_id,
                        action_id,
                        item["title"],
                        item["description"],
                        item["assigned_to"],
                        item.get("target_date"),
                        item["priority"]
                    )
                    print(f"[Retrospective] Created action item: {action_id}")
        except Exception as e:
            print(f"[Retrospective Error] Failed to store: {e}")
        
        # Send to Slack
        try:
            if self.slack.is_enabled():
                went_well_list = [item['text'] for item in self.feedback["went_well"][:3]]
                needs_improvement = [item['text'] for item in self.feedback["not_well"][:3]]
                
                self.slack.send_retrospective_summary(self.current_sprint, went_well_list, needs_improvement)
                
                if self.action_items_draft:
                    action_items_for_slack = [
                        {
                            "action_id": f"AI-{self.current_sprint:03d}-{item['number']:02d}",
                            "title": item["title"],
                            "assigned_to": item["assigned_to"],
                            "priority": item["priority"]
                        }
                        for item in self.action_items_draft
                    ]
                    self.slack.send_action_items_created(self.current_sprint, action_items_for_slack)
                    summary_text += "\n\n[Team has been notified on Slack!]"
        except Exception as e:
            print(f"[Retrospective Error] Slack failed: {e}")
        
        # Mark summary as generated
        self.summary_generated = True
        
        return {
            "summary_text": summary_text,
            "sentiment": self.team_sentiment,
            "action_items_count": len(self.action_items_draft)
        }
    
    def is_completed(self):
        """Check if retrospective is completed (summary generated)"""
        return self.summary_generated
    
    def end_retrospective(self):
        """End the retrospective session"""
        self.retro_started = False
        message = f"[RETROSPECTIVE ENDED] Sprint {self.current_sprint} retrospective has concluded."
        self.add_context("system", message)
        return message