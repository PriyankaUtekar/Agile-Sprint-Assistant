"""
Planning Agent - Manages sprint planning sessions
With completion tracking, story estimate clearing, and sprint status updates
"""
import sys
import os
import re

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from agents.base_agent import BaseAgent
from database.db_manager import DatabaseManager

class PlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.planning_started = False
        self.estimations = {}
        self.plan_approved = False
    
    def start_planning(self, session_id: str):
        """Start a new planning session"""
        self.session_id = session_id
        self.current_sprint = self.extract_sprint_number(session_id)
        self.planning_started = True
        self.plan_approved = False
        self.clear_context()
        self.estimations = {}
        
        # Get sprint info from database
        db = DatabaseManager()
        sprint = db.get_sprint(session_id)
        
        if not sprint:
            return f"[ERROR] Sprint '{session_id}' not found in database."
        
        message = f"""
[PLANNING STARTED]
Sprint: {self.current_sprint}
Goal: {sprint.sprint_goal}
Duration: {sprint.start_date} to {sprint.end_date}

Sprint Planning has begun. Let's estimate the user stories for this sprint!

The team can now provide story point estimates. The AI will offer its own estimate for comparison.
        """
        
        self.add_context("system", message)
        return message
    
    def estimate_story_with_comparison(self, story_id: str, team_estimate: int, team_reasoning: str, estimated_by: str):
        """
        Team provides an estimate, AI provides its own, then compare
        """
        if not self.planning_started:
            return {"error": "Planning session not started"}
        
        # Get story details from database
        db = DatabaseManager()
        sprint = db.get_sprint(self.session_id)
        if not sprint:
            return {"error": "Sprint not found"}
        
        stories = db.get_sprint_stories(sprint.id)
        story = next((s for s in stories if s.story_id == story_id), None)
        
        if not story:
            return {"error": f"Story {story_id} not found"}
        
        # Generate AI estimate with clear formatting instructions
        prompt = f"""
You are an experienced Scrum Master and technical lead. Estimate the story points for this user story.

Story ID: {story_id}
Title: {story.title}
Description: {story.description}
Acceptance Criteria: {story.acceptance_criteria}

The team's estimate: {team_estimate} points
Team's reasoning: {team_reasoning}

CRITICAL: You MUST start your response with EXACTLY this format on the first line:
AI_ESTIMATE: [number]

Where [number] must be ONE of these Fibonacci values: 1, 2, 3, 5, 8, or 13

Example:
AI_ESTIMATE: 8

Then on subsequent lines, provide:
1. Your reasoning for this estimate
2. A comparison with the team's estimate (explain if you agree or disagree and why)
3. Technical considerations that influenced your estimate
4. Any concerns or suggestions

Be specific and technical in your analysis.
        """
        
        ai_response = self.generate_response(prompt)
        
        # Extract AI's numeric estimate - IMPROVED PARSING
        ai_estimate = team_estimate  # Default to team estimate
        extraction_method = "default"
        
        # Method 1: Look for "AI_ESTIMATE: X" format (most reliable)
        if "AI_ESTIMATE:" in ai_response:
            match = re.search(r'AI_ESTIMATE:\s*(\d+)', ai_response, re.IGNORECASE)
            if match:
                try:
                    extracted = int(match.group(1))
                    if extracted in [1, 2, 3, 5, 8, 13]:
                        ai_estimate = extracted
                        extraction_method = "AI_ESTIMATE tag"
                        print(f"[Planning] Extracted AI estimate: {ai_estimate} (method: {extraction_method})")
                except:
                    pass
        
        # Method 2: Look for "**X points**" markdown pattern
        if ai_estimate == team_estimate:
            patterns = [
                r'\*\*(\d+)\s*points?\*\*',
                r'\*\*(\d+)-points?\*\*',
                r'estimate[:\s]+\*\*(\d+)',
                r'My\s+AI\s+estimate[:\s]+\*\*(\d+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, ai_response, re.IGNORECASE)
                if match:
                    try:
                        extracted = int(match.group(1))
                        if extracted in [1, 2, 3, 5, 8, 13]:
                            ai_estimate = extracted
                            extraction_method = f"markdown pattern"
                            print(f"[Planning] Extracted AI estimate: {ai_estimate} (method: {extraction_method})")
                            break
                    except:
                        pass
        
        # Method 3: Look in first 300 characters
        if ai_estimate == team_estimate:
            first_part = ai_response[:300].lower()
            for point in [13, 8, 5, 3, 2, 1]:
                point_patterns = [
                    f"{point} point",
                    f"{point}-point",
                    f"estimate {point}",
                    f"estimate: {point}",
                    f"estimate is {point}",
                ]
                for pt_pattern in point_patterns:
                    if pt_pattern in first_part:
                        ai_estimate = point
                        extraction_method = f"first 300 chars"
                        print(f"[Planning] Extracted AI estimate: {ai_estimate} (method: {extraction_method})")
                        break
                if ai_estimate != team_estimate:
                    break
        
        # Method 4: Look for common phrases
        if ai_estimate == team_estimate:
            phrases = [
                r'(?:my|ai)?\s*estimate[:\s]+is[:\s]+(\d+)',
                r'(?:recommend|suggest|propose)[:\s]+(\d+)\s+point',
                r'would\s+estimate[:\s]+(?:this\s+at[:\s]+)?(\d+)',
            ]
            for phrase in phrases:
                match = re.search(phrase, ai_response.lower())
                if match:
                    try:
                        extracted = int(match.group(1))
                        if extracted in [1, 2, 3, 5, 8, 13]:
                            ai_estimate = extracted
                            extraction_method = f"phrase pattern"
                            print(f"[Planning] Extracted AI estimate: {ai_estimate} (method: {extraction_method})")
                            break
                    except:
                        pass
        
        # Log if we couldn't extract a different estimate
        if ai_estimate == team_estimate:
            print(f"[Planning] WARNING: Could not extract AI estimate, defaulting to team estimate: {team_estimate}")
            print(f"[Planning] Response preview: {ai_response[:300]}...")
        
        # Store estimation data
        self.estimations[story_id] = {
            "team_estimate": team_estimate,
            "team_reasoning": team_reasoning,
            "estimated_by": estimated_by,
            "ai_estimate": ai_estimate,
            "ai_reasoning": ai_response,
            "extraction_method": extraction_method
        }
        
        comparison_message = f"""
[ESTIMATION COMPARISON]
Story: {story_id} - {story.title}

Team Estimate: {team_estimate} points
Estimated by: {estimated_by}
Team Reasoning: {team_reasoning}

AI Estimate & Analysis:
{ai_response}

Please review both estimates and choose which to use for final planning.
        """
        
        self.add_context("comparison", comparison_message)
        
        return {
            "comparison": comparison_message,
            "team_estimate": team_estimate,
            "agent_estimate": ai_estimate,
            "story_id": story_id
        }
    
    def finalize_story_estimate(self, story_id: str, accept_ai: bool):
        """
        Finalize the estimate after team reviews both
        """
        if story_id not in self.estimations:
            return f"[ERROR] No estimation data found for {story_id}"
        
        estimation = self.estimations[story_id]
        
        final_estimate = estimation["ai_estimate"] if accept_ai else estimation["team_estimate"]
        decision = "AI estimate" if accept_ai else "Team estimate"
        
        # Update story in database
        result = "[ERROR] Failed to update database"
        
        try:
            # Create new database manager
            db = DatabaseManager()
            
            # Get sprint
            sprint = db.get_sprint(self.session_id)
            if not sprint:
                return "[ERROR] Sprint not found"
            
            # Get all stories for this sprint
            stories = db.get_sprint_stories(sprint.id)
            story = next((s for s in stories if s.story_id == story_id), None)
            
            if story:
                # Update story attributes
                story.story_points = final_estimate
                story.story_points_approved = True
                
                committed = False
                
                # Method 1: Try SQLAlchemy inspection to get session
                try:
                    from sqlalchemy import inspect as sa_inspect
                    session = sa_inspect(story).session
                    if session:
                        session.commit()
                        committed = True
                        print(f"[Planning] Story {story_id} finalized: {final_estimate} points (using {decision})")
                except Exception as e1:
                    print(f"[Planning] Method 1 (inspection) failed: {e1}")
                
                # Method 2: Try accessing db manager's session
                if not committed:
                    try:
                        if hasattr(db, 'session'):
                            db.session.commit()
                            committed = True
                            print(f"[Planning] Story {story_id} finalized via session: {final_estimate} points")
                        elif hasattr(db, '_session'):
                            db._session.commit()
                            committed = True
                            print(f"[Planning] Story {story_id} finalized via _session: {final_estimate} points")
                    except Exception as e2:
                        print(f"[Planning] Method 2 (session attribute) failed: {e2}")
                
                # Method 3: Create new session with engine from models
                if not committed:
                    try:
                        from database.models import engine, UserStory
                        from sqlalchemy.orm import Session
                        
                        new_session = Session(bind=engine)
                        
                        # Query the story again in this new session
                        db_story = new_session.query(UserStory).filter(
                            UserStory.story_id == story_id
                        ).first()
                        
                        if db_story:
                            db_story.story_points = final_estimate
                            db_story.story_points_approved = True
                            new_session.commit()
                            committed = True
                            print(f"[Planning] Story {story_id} finalized via new session: {final_estimate} points")
                        
                        new_session.close()
                    except Exception as e3:
                        print(f"[Planning] Method 3 (new session) failed: {e3}")
                        import traceback
                        traceback.print_exc()
                
                if committed:
                    result = f"""
[ESTIMATE FINALIZED]
Story: {story_id}
Decision: Using {decision}
Final Points: {final_estimate}

Team Estimate: {estimation["team_estimate"]} points
AI Estimate: {estimation["ai_estimate"]} points
Chosen: {final_estimate} points

The estimate has been saved and the story is ready for the sprint!
                    """
                else:
                    result = "[ERROR] Could not commit changes to database - all methods failed"
            else:
                result = f"[ERROR] Story {story_id} not found in sprint stories"
                print(f"[Planning Error] {result}")
        except Exception as e:
            result = f"[ERROR] Failed to finalize estimate: {str(e)}"
            print(f"[Planning Error] {result}")
            import traceback
            traceback.print_exc()
        
        self.add_context("finalized", result)
        return result
    
    def generate_sprint_plan(self):
        """Generate comprehensive sprint plan"""
        if not self.planning_started:
            return {"error": "Planning session not started"}
        
        # Get sprint and stories from database
        db = DatabaseManager()
        sprint = db.get_sprint(self.session_id)
        if not sprint:
            return {"error": "Sprint not found"}
        
        stories = db.get_sprint_stories(sprint.id)
        
        # Build context
        stories_summary = ""
        total_points = 0
        approved_count = 0
        
        for story in stories:
            if story.story_points and story.story_points_approved:
                stories_summary += f"- {story.story_id}: {story.title} ({story.story_points} points)\n"
                total_points += story.story_points
                approved_count += 1
        
        if approved_count == 0:
            return {
                "error": "No approved stories found. Please estimate and approve stories first.",
                "plan_text": "[ERROR] Cannot generate plan without approved stories.",
                "total_points": 0,
                "story_count": 0
            }
        
        # Generate plan with AI
        prompt = f"""
You are an AI Scrum Master. Create a comprehensive sprint plan based on the following:

Sprint {self.current_sprint}
Goal: {sprint.sprint_goal}
Duration: {sprint.start_date} to {sprint.end_date}
Team: {sprint.team_name}

Approved Stories ({approved_count} stories, {total_points} points):
{stories_summary}

Create a detailed sprint plan that includes:

1. SPRINT OVERVIEW
   - Sprint goal recap
   - Total capacity and velocity
   - Key objectives

2. STORY BREAKDOWN
   - How to approach each story
   - Suggested order of implementation
   - Dependencies between stories

3. DAILY GOALS (estimate progress per day)
   - What should be completed each day
   - Milestones to hit

4. RISK ASSESSMENT
   - Potential risks and challenges
   - Mitigation strategies
   - Contingency plans

5. SUCCESS CRITERIA
   - What defines a successful sprint
   - Key deliverables
   - Quality standards

6. TEAM RECOMMENDATIONS
   - Communication strategies
   - Best practices for this sprint
   - Any special considerations

Format professionally with clear sections, bullet points, and actionable items.
        """
        
        plan_text = self.generate_response(prompt)
        
        # Store in database
        try:
            db.store_sprint_plan(self.session_id, plan_text)
            print(f"[Planning] Sprint plan stored in database")
        except Exception as e:
            print(f"[Planning Error] Failed to store plan: {e}")
        
        return {
            "plan_text": plan_text,
            "total_points": total_points,
            "story_count": approved_count
        }
    
    def approve_plan(self, scrum_master: str, comments: str = ""):
        """Approve sprint plan, send Slack notification, and update sprint status to active"""
        if not self.planning_started:
            return "[ERROR] Planning session not started"
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        approval_message = f"""
[PLAN APPROVED]
Approved by: {scrum_master} (Scrum Master)
Timestamp: {timestamp}
Comments: {comments if comments else "None"}

Sprint {self.current_sprint} planning is complete and approved!
The sprint status has been updated to ACTIVE.
The team is ready to start the sprint.
        """
        
        self.add_context("approved", approval_message)
        
        # Mark plan as approved
        self.plan_approved = True
        
        # Update sprint status to active
        try:
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            sprint = db.get_sprint(self.session_id)
            
            if sprint:
                # Update sprint status to active
                db.update_sprint_status(self.session_id, "active")
                print(f"[Planning] Sprint {self.current_sprint} status updated to ACTIVE")
                
                # Get sprint statistics for Slack
                try:
                    stories = db.get_sprint_stories(sprint.id)
                    approved_stories = [s for s in stories if s.story_points_approved]
                    total_points = sum(s.story_points for s in approved_stories if s.story_points)
                    
                    # Send to Slack
                    if self.slack.is_enabled():
                        slack_sent = self.slack.send_planning_complete(
                            self.current_sprint,
                            total_points,
                            len(approved_stories)
                        )
                        if slack_sent:
                            print(f"[Planning] Completion notification sent to Slack!")
                            approval_message += "\n\nTeam has been notified on Slack!"
                    else:
                        print("[Planning] Slack notifications disabled")
                except Exception as e:
                    print(f"[Planning Error] Failed to get sprint stats or send Slack: {e}")
            else:
                print(f"[Planning Error] Sprint {self.session_id} not found for status update")
                
        except Exception as e:
            print(f"[Planning Error] Failed to update sprint status: {e}")
            import traceback
            traceback.print_exc()
        
        return approval_message
    
    def is_completed(self):
        """Check if planning is completed (plan approved)"""
        return self.plan_approved
    
    def end_planning(self):
        """End the planning session"""
        self.planning_started = False
        message = f"[PLANNING ENDED] Sprint {self.current_sprint} planning session has concluded."
        self.add_context("system", message)
        return message