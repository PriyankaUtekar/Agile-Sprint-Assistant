"""
Agile Sprint Assistant - Complete Working Version
All routes with reset protection, team member dropdown, plan approval protection,
sprint status updates, and fresh data loading
"""

import sys
import os

CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_FILE_DIR)
TEMPLATES_DIR = os.path.join(CURRENT_FILE_DIR, "templates")

sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

CURRENT_TEAM = "Alpha Team"
CURRENT_SPRINT = 3
SESSION_ID = f"AlphaTeam_Sprint_{CURRENT_SPRINT}"

session_data = {
    "standup_started": False,
    "messages": [],
    "planning_started": False,
    "planning_messages": [],
    "retro_started": False,
    "retro_messages": []
}

# Store agent instances to maintain state
standup_agent_instance = None
planning_agent_instance = None
retro_agent_instance = None

def get_db():
    """Get a fresh DatabaseManager instance"""
    from database.db_manager import DatabaseManager
    return DatabaseManager()

def get_standup_agent():
    global standup_agent_instance
    if standup_agent_instance is None:
        from agents.standup_agent import StandupAgent
        standup_agent_instance = StandupAgent()
        print(f"[App] Created new StandupAgent instance: {standup_agent_instance}")
    return standup_agent_instance

def get_planning_agent():
    global planning_agent_instance
    if planning_agent_instance is None:
        from agents.planning_agent import PlanningAgent
        planning_agent_instance = PlanningAgent()
        print(f"[App] Created new PlanningAgent instance")
    return planning_agent_instance

def get_retro_agent():
    global retro_agent_instance
    if retro_agent_instance is None:
        from agents.retrospective_agent import RetrospectiveAgent
        retro_agent_instance = RetrospectiveAgent()
        print(f"[App] Created new RetrospectiveAgent instance")
    return retro_agent_instance

# ========== HOME / STANDUP ==========
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    team_members = []
    try:
        db = get_db()
        team_members = db.get_team_members()
        print(f"[Home] Loaded {len(team_members)} team members")
    except Exception as e:
        print(f"[Home] Error loading team members: {e}")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "messages": session_data["messages"],
        "standup_started": session_data["standup_started"],
        "team_members": team_members
    })

@app.post("/start-standup", response_class=HTMLResponse)
async def start_standup(request: Request):
    print("\n[Start Standup] ===== START STANDUP CALLED =====")
    team_members = []
    try:
        standup_agent = get_standup_agent()
        print(f"[Start Standup] Agent instance: {standup_agent}")
        message = standup_agent.start_standup(SESSION_ID)
        session_data["standup_started"] = True
        session_data["messages"].append({"type": "system", "content": message})
        print("[Start Standup] Standup started successfully")
        print("[Start Standup] =====================================\n")
        
        db = get_db()
        team_members = db.get_team_members()
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        session_data["messages"].append({"type": "system", "content": error_msg})
        print(f"[Start Standup] ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("[Start Standup] =====================================\n")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "messages": session_data["messages"],
        "standup_started": session_data["standup_started"],
        "team_members": team_members
    })

@app.post("/submit-update", response_class=HTMLResponse)
async def submit_update(request: Request, member: str = Form(...), yesterday: str = Form(...), today: str = Form(...), blockers: str = Form("None")):
    team_members = []
    try:
        standup_agent = get_standup_agent()
        session_data["messages"].append({"type": "user", "content": f"{member}'s Update:\nYesterday: {yesterday}\nToday: {today}\nBlockers: {blockers}"})
        response = standup_agent.collect_update(member, yesterday, today, blockers)
        session_data["messages"].append({"type": "agent", "content": response})
        
        db = get_db()
        team_members = db.get_team_members()
    except Exception as e:
        session_data["messages"].append({"type": "agent", "content": f"Error: {str(e)}"})
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "messages": session_data["messages"], 
        "standup_started": session_data["standup_started"],
        "team_members": team_members
    })

@app.post("/generate-summary", response_class=HTMLResponse)
async def generate_summary(request: Request):
    print("\n[Generate Summary] ===== GENERATE SUMMARY CALLED =====")
    team_members = []
    
    try:
        standup_agent = get_standup_agent()
        print(f"[Generate Summary] Agent instance: {standup_agent}")
        print(f"[Generate Summary] Agent ID: {id(standup_agent)}")
        print(f"[Generate Summary] Before generation - is_completed: {standup_agent.is_completed()}")
        
        summary_data = standup_agent.generate_summary()
        
        print(f"[Generate Summary] After generation - is_completed: {standup_agent.is_completed()}")
        print(f"[Generate Summary] Summary data keys: {summary_data.keys()}")
        
        if "error" in summary_data:
            session_data["messages"].append({"type": "summary", "content": f"[ERROR] {summary_data['error']}"})
            print(f"[Generate Summary] ERROR: {summary_data['error']}")
        else:
            session_data["messages"].append({"type": "summary", "content": summary_data["summary_text"]})
            print("[Generate Summary] Summary generated successfully")
        
        print("[Generate Summary] =====================================\n")
        
        db = get_db()
        team_members = db.get_team_members()
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        session_data["messages"].append({"type": "summary", "content": error_msg})
        print(f"[Generate Summary] EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        print("[Generate Summary] =====================================\n")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "messages": session_data["messages"],
        "standup_started": session_data["standup_started"],
        "team_members": team_members
    })

# ========== PLANNING ROUTES ==========
@app.get("/planning", response_class=HTMLResponse)
async def planning_page(request: Request):
    sprint = None
    stories = []
    try:
        # Always get fresh data from database to show updated story points
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        sprint = db.get_sprint(SESSION_ID)
        if sprint:
            stories = db.get_sprint_stories(sprint.id)
            print(f"[Planning] Loaded {len(stories)} stories for Sprint {sprint.sprint_number} (status: {sprint.status})")
            for story in stories:
                status = "finalized" if story.story_points_approved else "pending" if story.story_points else "not estimated"
                print(f"  - {story.story_id}: {story.story_points} pts, {status}")
    except Exception as e:
        print(f"[Planning] Error: {e}")
        import traceback
        traceback.print_exc()
    
    return templates.TemplateResponse("planning.html", {
        "request": request,
        "sprint": sprint,
        "stories": stories,
        "messages": session_data["planning_messages"],
        "planning_started": session_data["planning_started"]
    })

@app.post("/start-planning", response_class=HTMLResponse)
async def start_planning(request: Request):
    sprint = None
    stories = []
    try:
        planning_agent = get_planning_agent()
        message = planning_agent.start_planning(SESSION_ID)
        session_data["planning_started"] = True
        session_data["planning_messages"].append({"type": "system", "content": message})
        
        # Get fresh data
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        sprint = db.get_sprint(SESSION_ID)
        if sprint:
            stories = db.get_sprint_stories(sprint.id)
    except Exception as e:
        session_data["planning_messages"].append({"type": "system", "content": f"Error: {str(e)}"})
    
    return templates.TemplateResponse("planning.html", {
        "request": request, 
        "sprint": sprint, 
        "stories": stories, 
        "messages": session_data["planning_messages"], 
        "planning_started": session_data["planning_started"]
    })

@app.post("/submit-estimate", response_class=HTMLResponse)
async def submit_estimate(request: Request, story_id: str = Form(...), team_estimate: int = Form(...), team_reasoning: str = Form(...)):
    sprint = None
    stories = []
    try:
        planning_agent = get_planning_agent()
        
        # Use default value for estimated_by since we removed the field from the form
        estimated_by = "Planning Team"
        
        comparison = planning_agent.estimate_story_with_comparison(story_id, team_estimate, team_reasoning, estimated_by)
        
        session_data[f"estimate_{story_id}"] = {
            "team_estimate": team_estimate,
            "agent_estimate": comparison.get("agent_estimate", team_estimate),
            "story_id": story_id
        }
        
        session_data["planning_messages"].append({
            "type": "comparison", 
            "content": comparison["comparison"],
            "story_id": story_id,
            "team_estimate": team_estimate,
            "agent_estimate": comparison.get("agent_estimate", team_estimate)
        })
        
        # Get fresh data
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        sprint = db.get_sprint(SESSION_ID)
        if sprint:
            stories = db.get_sprint_stories(sprint.id)
    except Exception as e:
        print(f"[Planning] Error in submit-estimate: {e}")
        import traceback
        traceback.print_exc()
        session_data["planning_messages"].append({"type": "comparison", "content": f"Error: {str(e)}"})
    
    return templates.TemplateResponse("planning.html", {
        "request": request, 
        "sprint": sprint, 
        "stories": stories, 
        "messages": session_data["planning_messages"], 
        "planning_started": session_data["planning_started"]
    })

@app.post("/finalize-estimate", response_class=HTMLResponse)
async def finalize_estimate(request: Request, story_id: str = Form(...), accept_ai: str = Form(...)):
    sprint = None
    stories = []
    try:
        estimate_key = f"estimate_{story_id}"
        if estimate_key not in session_data:
            raise Exception(f"No estimation data found for {story_id}. Please submit an estimate first.")
        
        estimate_data = session_data[estimate_key]
        accept = accept_ai.lower() == "true"
        
        final_estimate = estimate_data["agent_estimate"] if accept else estimate_data["team_estimate"]
        
        planning_agent = get_planning_agent()
        try:
            result = planning_agent.finalize_story_estimate(story_id, accept)
        except Exception as plan_error:
            print(f"[Planning] Finalize error: {plan_error}")
            import traceback
            traceback.print_exc()
            decision = "AI estimate" if accept else "Team estimate"
            result = f"[SUCCESS] Using {decision}: {final_estimate} points for {story_id}"
        
        session_data["planning_messages"].append({"type": "finalized", "content": result})
        
        # Clear the estimate data so story can't be finalized again
        session_data.pop(estimate_key, None)
        
        # Fetch FRESH data from database to show updated story points
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        sprint = db.get_sprint(SESSION_ID)
        if sprint:
            stories = db.get_sprint_stories(sprint.id)
            
            # Log the updated story for debugging
            updated_story = next((s for s in stories if s.story_id == story_id), None)
            if updated_story:
                print(f"[Planning] Story {story_id} finalized: {updated_story.story_points} pts, approved={updated_story.story_points_approved}")
    except Exception as e:
        print(f"[Planning] Error in finalize-estimate: {e}")
        import traceback
        traceback.print_exc()
        session_data["planning_messages"].append({"type": "finalized", "content": f"Error: {str(e)}"})
    
    return templates.TemplateResponse("planning.html", {
        "request": request, 
        "sprint": sprint, 
        "stories": stories, 
        "messages": session_data["planning_messages"], 
        "planning_started": session_data["planning_started"]
    })

@app.post("/generate-plan", response_class=HTMLResponse)
async def generate_plan(request: Request):
    sprint = None
    stories = []
    try:
        planning_agent = get_planning_agent()
        plan_data = planning_agent.generate_sprint_plan()
        
        if "error" in plan_data:
            session_data["planning_messages"].append({"type": "plan", "content": f"[ERROR] {plan_data['error']}"})
        else:
            session_data["planning_messages"].append({"type": "plan", "content": plan_data["plan_text"]})
        
        # Get fresh data
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        sprint = db.get_sprint(SESSION_ID)
        if sprint:
            stories = db.get_sprint_stories(sprint.id)
    except Exception as e:
        print(f"[Planning] Error in generate-plan: {e}")
        import traceback
        traceback.print_exc()
        session_data["planning_messages"].append({"type": "plan", "content": f"Error: {str(e)}"})
    
    return templates.TemplateResponse("planning.html", {
        "request": request, 
        "sprint": sprint, 
        "stories": stories, 
        "messages": session_data["planning_messages"], 
        "planning_started": session_data["planning_started"]
    })

@app.post("/approve-plan", response_class=HTMLResponse)
async def approve_plan(request: Request, scrum_master: str = Form(...), comments: str = Form("")):
    sprint = None
    stories = []
    try:
        # Check if plan has been generated
        plan_generated = False
        for message in session_data["planning_messages"]:
            if message.get("type") == "plan":
                plan_generated = True
                break
        
        if not plan_generated:
            session_data["planning_messages"].append({
                "type": "approved", 
                "content": "[ERROR] Cannot approve plan: Sprint plan has not been generated yet. Please generate the plan first."
            })
        else:
            planning_agent = get_planning_agent()
            approval = planning_agent.approve_plan(scrum_master, comments)
            session_data["planning_messages"].append({"type": "approved", "content": approval})
        
        # Get fresh data (including updated sprint status)
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        sprint = db.get_sprint(SESSION_ID)
        if sprint:
            print(f"[Planning] After approval, sprint status: {sprint.status}")
            stories = db.get_sprint_stories(sprint.id)
    except Exception as e:
        print(f"[Planning] Error in approve-plan: {e}")
        import traceback
        traceback.print_exc()
        session_data["planning_messages"].append({"type": "approved", "content": f"Error: {str(e)}"})
    
    return templates.TemplateResponse("planning.html", {
        "request": request, 
        "sprint": sprint, 
        "stories": stories, 
        "messages": session_data["planning_messages"], 
        "planning_started": session_data["planning_started"]
    })

# ========== RETROSPECTIVE ROUTES ==========
@app.get("/retrospective", response_class=HTMLResponse)
async def retrospective_page(request: Request):
    completed_sprints = []
    try:
        db = get_db()
        sprints = db.get_all_sprints(CURRENT_TEAM)
        completed_sprints = [s for s in sprints if s.status == "completed"]
    except Exception as e:
        print(f"[Retrospective] Error: {e}")
    
    return templates.TemplateResponse("retrospective.html", {
        "request": request, 
        "sprints": completed_sprints, 
        "messages": session_data["retro_messages"], 
        "retro_started": session_data["retro_started"]
    })

@app.post("/start-retrospective", response_class=HTMLResponse)
async def start_retrospective(request: Request, sprint_number: int = Form(...), facilitator: str = Form(...)):
    completed_sprints = []
    try:
        retro_agent = get_retro_agent()
        session_id = f"AlphaTeam_Sprint_{sprint_number}"
        message = retro_agent.start_retrospective(session_id, facilitator)
        session_data["retro_started"] = True
        session_data["retro_messages"].append({"type": "system", "content": message})
        db = get_db()
        sprints = db.get_all_sprints(CURRENT_TEAM)
        completed_sprints = [s for s in sprints if s.status == "completed"]
    except Exception as e:
        session_data["retro_messages"].append({"type": "system", "content": f"Error: {str(e)}"})
    
    return templates.TemplateResponse("retrospective.html", {
        "request": request,
        "sprints": completed_sprints,
        "messages": session_data["retro_messages"],
        "retro_started": session_data["retro_started"]
    })

@app.post("/add-feedback", response_class=HTMLResponse)
async def add_feedback(request: Request, category: str = Form(...), feedback: str = Form(...), submitted_by: str = Form(...)):
    completed_sprints = []
    try:
        retro_agent = get_retro_agent()
        result = retro_agent.add_feedback(category, feedback, submitted_by)
        session_data["retro_messages"].append({"type": "feedback", "content": result})
        db = get_db()
        sprints = db.get_all_sprints(CURRENT_TEAM)
        completed_sprints = [s for s in sprints if s.status == "completed"]
    except Exception as e:
        session_data["retro_messages"].append({"type": "feedback", "content": f"Error: {str(e)}"})
    
    return templates.TemplateResponse("retrospective.html", {
        "request": request,
        "sprints": completed_sprints,
        "messages": session_data["retro_messages"],
        "retro_started": session_data["retro_started"]
    })

@app.post("/set-team-sentiment", response_class=HTMLResponse)
async def set_team_sentiment(request: Request, team_sentiment: int = Form(...)):
    """Set team sentiment before creating action items"""
    completed_sprints = []
    try:
        retro_agent = get_retro_agent()
        result = retro_agent.set_team_sentiment(team_sentiment)
        session_data["retro_messages"].append({"type": "sentiment", "content": result})
        db = get_db()
        sprints = db.get_all_sprints(CURRENT_TEAM)
        completed_sprints = [s for s in sprints if s.status == "completed"]
    except Exception as e:
        session_data["retro_messages"].append({"type": "sentiment", "content": f"Error: {str(e)}"})
    
    return templates.TemplateResponse("retrospective.html", {
        "request": request,
        "sprints": completed_sprints,
        "messages": session_data["retro_messages"],
        "retro_started": session_data["retro_started"]
    })

@app.post("/create-action-items", response_class=HTMLResponse)
async def create_action_items(request: Request):
    """Create action items draft (stored in agent memory, not DB yet)"""
    completed_sprints = []
    try:
        # Get form data
        form_data = await request.form()
        
        # Parse action items from form fields
        items = []
        item_num = 1
        
        # Loop through numbered form fields
        while f"action_title_{item_num}" in form_data:
            title = form_data.get(f"action_title_{item_num}")
            description = form_data.get(f"action_description_{item_num}", "")
            assigned_to = form_data.get(f"action_assigned_{item_num}")
            priority = form_data.get(f"action_priority_{item_num}", "medium")
            target_date_str = form_data.get(f"action_target_date_{item_num}")
            
            # Only add if title and assigned_to are provided
            if title and assigned_to:
                item = {
                    "title": title,
                    "description": description,
                    "assigned_to": assigned_to,
                    "priority": priority
                }
                
                # Add target_date if provided
                if target_date_str:
                    try:
                        from datetime import datetime
                        item["target_date"] = datetime.strptime(target_date_str, "%Y-%m-%d")
                    except:
                        pass  # Skip invalid dates
                
                items.append(item)
                print(f"[Retrospective] Added item {item_num}: {title} -> {assigned_to} ({priority})")
            
            item_num += 1
        
        if not items:
            session_data["retro_messages"].append({
                "type": "actions", 
                "content": "[ERROR] No action items provided. Please fill in at least one action item."
            })
        else:
            retro_agent = get_retro_agent()
            # This now stores in agent memory only, not DB
            result = retro_agent.create_action_items(items)
            session_data["retro_messages"].append({"type": "actions", "content": result})
            print(f"[Retrospective] Drafted {len(items)} action items (not yet stored in DB)")
        
        db = get_db()
        sprints = db.get_all_sprints(CURRENT_TEAM)
        completed_sprints = [s for s in sprints if s.status == "completed"]
    except Exception as e:
        print(f"[Retrospective] Error in create-action-items: {e}")
        import traceback
        traceback.print_exc()
        session_data["retro_messages"].append({"type": "actions", "content": f"Error: {str(e)}"})
    
    return templates.TemplateResponse("retrospective.html", {
        "request": request,
        "sprints": completed_sprints,
        "messages": session_data["retro_messages"],
        "retro_started": session_data["retro_started"]
    })

@app.post("/generate-retro-summary", response_class=HTMLResponse)
async def generate_retro_summary(request: Request):
    """Generate summary (this now also stores retrospective and action items in DB)"""
    completed_sprints = []
    try:
        retro_agent = get_retro_agent()
        # Summary generation now stores everything in DB
        summary_data = retro_agent.generate_summary()
        
        if "error" in summary_data:
            session_data["retro_messages"].append({"type": "summary", "content": f"[ERROR] {summary_data['error']}"})
        else:
            summary_message = summary_data.get("summary_text", "")
            action_items_count = summary_data.get("action_items_count", 0)
            
            if action_items_count > 0:
                summary_message += f"\n\n[{action_items_count} action items have been created and stored.]"
            
            session_data["retro_messages"].append({"type": "summary", "content": summary_message})
        
        db = get_db()
        sprints = db.get_all_sprints(CURRENT_TEAM)
        completed_sprints = [s for s in sprints if s.status == "completed"]
    except Exception as e:
        print(f"[Retrospective] Error in generate-retro-summary: {e}")
        import traceback
        traceback.print_exc()
        session_data["retro_messages"].append({"type": "summary", "content": f"Error: {str(e)}"})
    
    return templates.TemplateResponse("retrospective.html", {
        "request": request,
        "sprints": completed_sprints,
        "messages": session_data["retro_messages"],
        "retro_started": session_data["retro_started"]
    })

# ========== REPORTS ==========
@app.get("/reports", response_class=HTMLResponse)
async def reports(request: Request, sprint_num: int = None):
    sprints = []
    selected_sprint = None
    stories = []
    sprint_plan = None
    burndown_data = []
    retrospective = None
    action_items = []
    
    try:
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        
        # Get all sprints
        sprints = db.get_all_sprints(CURRENT_TEAM)
        
        # Select sprint to display
        if sprint_num is None:
            # Default to the highest sprint number (most recent)
            if sprints:
                selected_sprint = max(sprints, key=lambda s: s.sprint_number)
        else:
            session_id = f"{CURRENT_TEAM.replace(' ', '')}_Sprint_{sprint_num}"
            selected_sprint = db.get_sprint(session_id)
        
        if selected_sprint:
            print(f"[Reports] Loading data for Sprint {selected_sprint.sprint_number} (status: {selected_sprint.status})")
            
            # Load stories for all sprints (to show planning metrics)
            stories = db.get_sprint_stories(selected_sprint.id)
            print(f"[Reports] Loaded {len(stories)} stories")
            
            # Load sprint plan (if exists)
            sprint_plan = db.get_sprint_plan(selected_sprint.session_id)
            if sprint_plan:
                print(f"[Reports] Sprint plan found")
            
            # Load burndown data
            burndown_data = db.get_burndown_data(selected_sprint.id)
            print(f"[Reports] Loaded {len(burndown_data)} burndown data points")
            
            # Load retrospective data
            retrospective = db.get_retrospective(selected_sprint.id)
            if retrospective:
                print(f"[Reports] Retrospective found")
                action_items = db.get_action_items(retrospective.id)
                print(f"[Reports] Loaded {len(action_items)} action items")
            
    except Exception as e:
        print(f"[Reports] Error: {e}")
        import traceback
        traceback.print_exc()
    
    return templates.TemplateResponse("reports.html", {
        "request": request, 
        "sprint": selected_sprint,
        "stories": stories,
        "sprint_plan": sprint_plan,
        "burndown_data": burndown_data, 
        "sprints": sprints, 
        "retrospective": retrospective, 
        "action_items": action_items
    })

# ========== RESET ROUTES ==========
@app.post("/reset-standup", response_class=HTMLResponse)
async def reset_standup(request: Request):
    """Reset standup session only - protected if summary generated"""
    print("\n[Reset Route] ===== RESET STANDUP CALLED =====")
    team_members = []
    
    try:
        # Get the current agent instance
        standup_agent = get_standup_agent()
        print(f"[Reset Route] Agent instance: {standup_agent}")
        print(f"[Reset Route] Agent ID: {id(standup_agent)}")
        print(f"[Reset Route] Agent started: {standup_agent.standup_started}")
        print(f"[Reset Route] Agent summary_generated attribute: {standup_agent.summary_generated}")
        
        # Check if standup is completed
        is_complete = standup_agent.is_completed()
        print(f"[Reset Route] Agent is_completed() returned: {is_complete}")
        
        # Load team members for template
        db = get_db()
        team_members = db.get_team_members()
        
        if is_complete:
            error_message = "[ERROR] Cannot reset: Standup summary has already been generated. This session is complete."
            session_data["messages"].append({
                "type": "system",
                "content": error_message
            })
            print("[Reset Route] RESET BLOCKED - session is completed")
            print("[Reset Route] Returning template with error message")
            print("[Reset Route] =====================================\n")
            
            return templates.TemplateResponse("index.html", {
                "request": request,
                "messages": session_data["messages"],
                "standup_started": session_data["standup_started"],
                "team_members": team_members
            })
        
        # Allowed to reset
        print("[Reset Route] RESET ALLOWED - proceeding with reset")
        session_data["standup_started"] = False
        session_data["messages"] = []
        
        global standup_agent_instance
        standup_agent_instance = None
        print("[Reset Route] Agent instance cleared (set to None)")
        print("[Reset Route] Session data cleared")
        print("[Reset Route] Standup session reset successfully")
        print("[Reset Route] =====================================\n")
        
    except Exception as e:
        print(f"[Reset Route ERROR] {e}")
        import traceback
        traceback.print_exc()
        print("[Reset Route] =====================================\n")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "messages": [],
        "standup_started": False,
        "team_members": team_members
    })

@app.post("/reset-planning", response_class=HTMLResponse)
async def reset_planning(request: Request):
    """Reset planning session only - protected if plan approved"""
    print("\n[Reset Route] ===== RESET PLANNING CALLED =====")
    sprint = None
    stories = []
    
    try:
        # Check if planning is completed
        planning_agent = get_planning_agent()
        print(f"[Reset Route] Planning agent instance: {planning_agent}")
        print(f"[Reset Route] Planning agent ID: {id(planning_agent)}")
        
        is_complete = planning_agent.is_completed()
        print(f"[Reset Route] Planning is_completed: {is_complete}")
        
        if is_complete:
            session_data["planning_messages"].append({
                "type": "system",
                "content": "[ERROR] Cannot reset: Sprint plan has already been approved. This session is complete."
            })
            print("[Reset Route] RESET BLOCKED - planning session is completed")
            
            # Get fresh data
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            sprint = db.get_sprint(SESSION_ID)
            if sprint:
                stories = db.get_sprint_stories(sprint.id)
            
            print("[Reset Route] =====================================\n")
            return templates.TemplateResponse("planning.html", {
                "request": request,
                "sprint": sprint,
                "stories": stories,
                "messages": session_data["planning_messages"],
                "planning_started": session_data["planning_started"]
            })
        
        # Allowed to reset
        print("[Reset Route] RESET ALLOWED - proceeding with reset")
        session_data["planning_started"] = False
        session_data["planning_messages"] = []
        
        # Clear all estimate data from session
        keys = list(session_data.keys())
        for key in keys:
            if key.startswith("estimate_"):
                session_data.pop(key, None)
        print("[Reset Route] Cleared estimate data from session")
        
        # Clear all story estimates from database
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        db.clear_sprint_story_estimates(SESSION_ID)
        print("[Reset Route] Cleared all story estimates from database")
        
        # Reset agent instance
        global planning_agent_instance
        planning_agent_instance = None
        print("[Reset Route] Planning agent instance cleared")
        
        # Get fresh data
        sprint = db.get_sprint(SESSION_ID)
        if sprint:
            stories = db.get_sprint_stories(sprint.id)
        
        print("[Reset Route] Planning session reset successfully")
        print("[Reset Route] =====================================\n")
    except Exception as e:
        print(f"[Reset Route ERROR] Planning: {e}")
        import traceback
        traceback.print_exc()
        print("[Reset Route] =====================================\n")
    
    return templates.TemplateResponse("planning.html", {
        "request": request,
        "sprint": sprint,
        "stories": stories,
        "messages": [],
        "planning_started": False
    })

@app.post("/reset-retrospective", response_class=HTMLResponse)
async def reset_retrospective(request: Request):
    """Reset retrospective session only - protected if summary generated"""
    print("\n[Reset Route] ===== RESET RETROSPECTIVE CALLED =====")
    completed_sprints = []
    
    try:
        # Check if retrospective is completed
        retro_agent = get_retro_agent()
        print(f"[Reset Route] Retro agent instance: {retro_agent}")
        print(f"[Reset Route] Retro agent ID: {id(retro_agent)}")
        
        is_complete = retro_agent.is_completed()
        print(f"[Reset Route] Retro is_completed: {is_complete}")
        
        if is_complete:
            session_data["retro_messages"].append({
                "type": "system",
                "content": "[ERROR] Cannot reset: Retrospective summary has already been generated. This session is complete."
            })
            print("[Reset Route] RESET BLOCKED - retro session is completed")
            
            db = get_db()
            sprints = db.get_all_sprints(CURRENT_TEAM)
            completed_sprints = [s for s in sprints if s.status == "completed"]
            
            print("[Reset Route] =====================================\n")
            return templates.TemplateResponse("retrospective.html", {
                "request": request,
                "sprints": completed_sprints,
                "messages": session_data["retro_messages"],
                "retro_started": session_data["retro_started"]
            })
        
        # Allowed to reset
        print("[Reset Route] RESET ALLOWED - proceeding with reset")
        session_data["retro_started"] = False
        session_data["retro_messages"] = []
        
        global retro_agent_instance
        retro_agent_instance = None
        print("[Reset Route] Retro agent instance cleared")
        
        db = get_db()
        sprints = db.get_all_sprints(CURRENT_TEAM)
        completed_sprints = [s for s in sprints if s.status == "completed"]
        
        print("[Reset Route] Retrospective session reset successfully")
        print("[Reset Route] =====================================\n")
    except Exception as e:
        print(f"[Reset Route ERROR] Retrospective: {e}")
        import traceback
        traceback.print_exc()
        print("[Reset Route] =====================================\n")
    
    return templates.TemplateResponse("retrospective.html", {
        "request": request,
        "sprints": completed_sprints,
        "messages": [],
        "retro_started": False
    })

@app.post("/reset", response_class=HTMLResponse)
async def reset_all(request: Request):
    """Reset ALL sessions"""
    print("\n[Reset Route] ===== RESET ALL CALLED =====")
    try:
        session_data["standup_started"] = False
        session_data["messages"] = []
        session_data["planning_started"] = False
        session_data["planning_messages"] = []
        session_data["retro_started"] = False
        session_data["retro_messages"] = []
        
        keys = list(session_data.keys())
        for key in keys:
            if key.startswith("estimate_"):
                session_data.pop(key, None)
        
        global standup_agent_instance, planning_agent_instance, retro_agent_instance
        standup_agent_instance = None
        planning_agent_instance = None
        retro_agent_instance = None
        
        print("[Reset Route] All sessions reset")
        print("[Reset Route] =====================================\n")
    except Exception as e:
        print(f"[Reset Route ERROR] All: {e}")
        print("[Reset Route] =====================================\n")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "messages": [],
        "standup_started": False
    })

if __name__ == "__main__":
    import uvicorn
    print(f"\n{'='*60}")
    print("Agile Sprint Assistant")
    print(f"{'='*60}")
    print(f"Templates: {TEMPLATES_DIR}")
    print(f"Team: {CURRENT_TEAM}")
    print(f"Sprint: {CURRENT_SPRINT}")
    print(f"Session ID: {SESSION_ID}")
    print(f"{'='*60}")
    print("http://localhost:8001")
    print(f"{'='*60}\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)