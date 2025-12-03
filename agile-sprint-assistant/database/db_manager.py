"""
Database Manager - Handles all database operations
Complete version with all fixes and enhancements
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import (
    Base, SprintSession, UserStory, DailyStandup, 
    Retrospective, ActionItem, BurndownData, 
    Risk, Issue, Dependency, SprintCapacity, TeamMember
)
from datetime import datetime, timedelta
import json

class DatabaseManager:
    def __init__(self, db_path: str = "sqlite:///database/agile_assistant.db"):
        """Initialize database connection"""
        self.engine = create_engine(db_path, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'session'):
            self.session.close()
    
    # ========== SPRINT MANAGEMENT ==========
    
    def create_sprint(self, session_id: str, team_name: str, sprint_number: int,
                     start_date: datetime, end_date: datetime, sprint_goal: str,
                     total_capacity: int = 80):
        """Create a new sprint session"""
        sprint = SprintSession(
            session_id=session_id,
            team_name=team_name,
            sprint_number=sprint_number,
            start_date=start_date,
            end_date=end_date,
            sprint_goal=sprint_goal,
            status="active",
            total_capacity=total_capacity,
            remaining_capacity=total_capacity,
            planned_points=0,
            completed_points=0
        )
        self.session.add(sprint)
        self.session.commit()
        return sprint
    
    def get_sprint(self, session_id: str):
        """Get sprint by session ID"""
        return self.session.query(SprintSession).filter(
            SprintSession.session_id == session_id
        ).first()
    
    def get_all_sprints(self, team_name: str):
        """Get all sprints for a team"""
        return self.session.query(SprintSession).filter(
            SprintSession.team_name == team_name
        ).order_by(SprintSession.sprint_number).all()
    
    def update_sprint_status(self, session_id: str, status: str):
        """Update sprint status"""
        sprint = self.get_sprint(session_id)
        if sprint:
            sprint.status = status
            sprint.updated_at = datetime.now()
            self.session.commit()
            print(f"[Database] Updated sprint {session_id} status to: {status}")
            return True
        return False
    
    # ========== USER STORY MANAGEMENT ==========
    
    def create_story(self, sprint_id: int, story_id: str, title: str,
                    description: str, acceptance_criteria: str,
                    story_type: str = "feature", priority: str = "medium"):
        """Create a new user story"""
        story = UserStory(
            sprint_id=sprint_id,
            story_id=story_id,
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            story_type=story_type,
            priority=priority,
            status="backlog"
        )
        self.session.add(story)
        self.session.commit()
        return story
    
    def get_sprint_stories(self, sprint_id: int):
        """Get all stories for a sprint"""
        return self.session.query(UserStory).filter(
            UserStory.sprint_id == sprint_id
        ).all()
    
    def update_story_estimate(self, story_id: str, story_points: int, approved: bool = False):
        """Update story point estimate"""
        story = self.session.query(UserStory).filter(
            UserStory.story_id == story_id
        ).first()
        if story:
            story.story_points = story_points
            story.story_points_approved = approved
            self.session.commit()
            return True
        return False
    
    def clear_sprint_story_estimates(self, session_id: str):
        """
        Clear all story estimates for a sprint (for planning reset)
        Sets story_points to None and story_points_approved to False
        """
        try:
            sprint = self.get_sprint(session_id)
            if not sprint:
                print(f"[Database] Sprint {session_id} not found for estimate clearing")
                return False
            
            stories = self.get_sprint_stories(sprint.id)
            
            cleared_count = 0
            for story in stories:
                if story.story_points is not None or story.story_points_approved:
                    story.story_points = None
                    story.story_points_approved = False
                    cleared_count += 1
            
            self.session.commit()
            print(f"[Database] Cleared estimates for {cleared_count} stories in {session_id}")
            return True
        except Exception as e:
            self.session.rollback()
            print(f"[Database Error] Failed to clear story estimates: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== DAILY STANDUP ==========
    
    def store_standup(self, sprint_id: int, member_name: str, yesterday: str,
                     today: str, blockers: str, hours_worked: float = 0.0):
        """Store a daily standup update"""
        standup = DailyStandup(
            sprint_id=sprint_id,
            standup_date=datetime.now().date(),
            member_name=member_name,
            yesterday=yesterday,
            today=today,
            blockers=blockers,
            hours_worked=hours_worked
        )
        self.session.add(standup)
        self.session.commit()
        return standup
    
    def get_standup_history(self, sprint_id: int, days: int = 7):
        """Get standup history for last N days"""
        cutoff_date = datetime.now().date() - timedelta(days=days)
        return self.session.query(DailyStandup).filter(
            DailyStandup.sprint_id == sprint_id,
            DailyStandup.standup_date >= cutoff_date
        ).order_by(DailyStandup.standup_date.desc()).all()
    
    # ========== RETROSPECTIVE ==========
    
    def store_retrospective(self, session_id: str, facilitator: str,
                          went_well: list, not_well: list, improve: list,
                          summary: str, team_sentiment: int):
        """Store retrospective data"""
        sprint = self.get_sprint(session_id)
        if not sprint:
            raise ValueError(f"Sprint {session_id} not found")
        
        retro = Retrospective(
            sprint_session_id=sprint.id,
            retro_date=datetime.now().date(),
            facilitator=facilitator,
            what_went_well=json.dumps(went_well),
            what_didnt_go_well=json.dumps(not_well),
            what_to_improve=json.dumps(improve),
            summary=summary,
            team_sentiment=team_sentiment
        )
        self.session.add(retro)
        self.session.commit()
        return retro.id
    
    def get_retrospective(self, sprint_id: int):
        """Get retrospective for a sprint"""
        retro = self.session.query(Retrospective).filter(
            Retrospective.sprint_session_id == sprint_id
        ).first()
        
        if retro:
            # Parse JSON fields
            try:
                retro.what_went_well = json.loads(retro.what_went_well) if retro.what_went_well else []
            except:
                retro.what_went_well = []
            
            try:
                retro.what_didnt_go_well = json.loads(retro.what_didnt_go_well) if retro.what_didnt_go_well else []
            except:
                retro.what_didnt_go_well = []
            
            try:
                retro.what_to_improve = json.loads(retro.what_to_improve) if retro.what_to_improve else []
            except:
                retro.what_to_improve = []
        
        return retro
    
    # ========== ACTION ITEMS ==========
    
    def store_action_item(self, retrospective_id: int, action_id: str,
                         title: str, description: str, assigned_to: str,
                         target_date: datetime = None, priority: str = "medium"):
        """Store an action item from retrospective"""
        action = ActionItem(
            retrospective_id=retrospective_id,
            action_id=action_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            target_date=target_date,
            priority=priority,
            status="open"
        )
        self.session.add(action)
        self.session.commit()
        return action
    
    def get_action_items(self, retrospective_id: int):
        """Get all action items for a retrospective"""
        return self.session.query(ActionItem).filter(
            ActionItem.retrospective_id == retrospective_id
        ).all()
    
    def update_action_item_status(self, action_id: str, status: str):
        """Update action item status"""
        action = self.session.query(ActionItem).filter(
            ActionItem.action_id == action_id
        ).first()
        if action:
            action.status = status
            if status == "completed":
                action.completed_at = datetime.now()
            self.session.commit()
            return True
        return False
    
    # ========== BURNDOWN DATA ==========
    
    def store_burndown_data(self, sprint_id: int, date: datetime,
                           remaining_points: int, completed_points: int,
                           ideal_remaining: float):
        """Store burndown chart data point"""
        burndown = BurndownData(
            sprint_id=sprint_id,
            date=date.date(),
            remaining_points=remaining_points,
            completed_points=completed_points,
            ideal_remaining=ideal_remaining,
            stories_completed=0,
            stories_in_progress=0,
            stories_blocked=0
        )
        self.session.add(burndown)
        self.session.commit()
        return burndown
    
    def get_burndown_data(self, sprint_id: int):
        """Get all burndown data for a sprint"""
        return self.session.query(BurndownData).filter(
            BurndownData.sprint_id == sprint_id
        ).order_by(BurndownData.date).all()
    
    # ========== RISKS ==========
    
    def create_risk(self, sprint_id: int, risk_id: str, title: str,
                   description: str, probability: str, impact: str,
                   mitigation_plan: str, owner: str):
        """Create a risk"""
        risk = Risk(
            sprint_session_id=sprint_id,
            risk_id=risk_id,
            title=title,
            description=description,
            probability=probability,
            impact=impact,
            severity=self._calculate_severity(probability, impact),
            mitigation_plan=mitigation_plan,
            owner=owner,
            status="open"
        )
        self.session.add(risk)
        self.session.commit()
        return risk
    
    def _calculate_severity(self, probability: str, impact: str):
        """Calculate risk severity from probability and impact"""
        score = 0
        prob_map = {"low": 1, "medium": 2, "high": 3}
        impact_map = {"low": 1, "medium": 2, "high": 3}
        
        score = prob_map.get(probability.lower(), 1) * impact_map.get(impact.lower(), 1)
        
        if score >= 6:
            return "critical"
        elif score >= 4:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"
    
    # ========== ISSUES ==========
    
    def create_issue(self, sprint_id: int, issue_id: str, title: str,
                    description: str, issue_type: str, severity: str,
                    reported_by: str, assigned_to: str = None):
        """Create an issue"""
        issue = Issue(
            sprint_session_id=sprint_id,
            issue_id=issue_id,
            title=title,
            description=description,
            issue_type=issue_type,
            severity=severity,
            reported_by=reported_by,
            assigned_to=assigned_to,
            status="open"
        )
        self.session.add(issue)
        self.session.commit()
        return issue
    
    # ========== SPRINT PLAN ==========
    
    def store_sprint_plan(self, session_id: str, plan_text: str):
        """Store sprint plan in sprint state"""
        sprint = self.get_sprint(session_id)
        if sprint:
            try:
                state = json.loads(sprint.state) if sprint.state else {}
            except:
                state = {}
            
            state['plan'] = plan_text
            state['plan_created_at'] = datetime.now().isoformat()
            sprint.state = json.dumps(state)
            self.session.commit()
            return True
        return False
    
    def get_sprint_plan(self, session_id: str):
        """Get sprint plan from sprint state"""
        sprint = self.get_sprint(session_id)
        if sprint and sprint.state:
            try:
                state = json.loads(sprint.state)
                return state.get('plan')
            except:
                return None
        return None
    
    # ========== TEAM MEMBERS ==========
    
    def create_team_member(self, name: str, role: str, email: str = None,
                          default_capacity: int = 40, skills: list = None):
        """Create a team member"""
        member = TeamMember(
            name=name,
            role=role,
            email=email,
            default_capacity=default_capacity,
            skills=json.dumps(skills) if skills else "[]"
        )
        self.session.add(member)
        self.session.commit()
        return member
    
    def get_team_members(self):
        """Get all team members with proper error handling"""
        try:
            members = self.session.query(TeamMember).all()
            for member in members:
                # Handle skills field - could be string, list, or None
                if member.skills:
                    if isinstance(member.skills, str):
                        try:
                            member.skills = json.loads(member.skills)
                        except json.JSONDecodeError:
                            print(f"[Database Warning] Invalid JSON in skills for {member.name}, setting to empty list")
                            member.skills = []
                    elif isinstance(member.skills, list):
                        # Already a list, no conversion needed
                        pass
                    else:
                        # Unknown type, set to empty list
                        member.skills = []
                else:
                    member.skills = []
            return members
        except Exception as e:
            print(f"[Database Error] Failed to get team members: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_team_member_by_name(self, name: str):
        """Get a specific team member by name"""
        try:
            member = self.session.query(TeamMember).filter(
                TeamMember.name == name
            ).first()
            
            if member and member.skills:
                if isinstance(member.skills, str):
                    try:
                        member.skills = json.loads(member.skills)
                    except:
                        member.skills = []
                elif not isinstance(member.skills, list):
                    member.skills = []
            elif member:
                member.skills = []
            
            return member
        except Exception as e:
            print(f"[Database Error] Failed to get team member {name}: {e}")
            return None
    
    # ========== SPRINT CAPACITY ==========
    
    def set_sprint_capacity(self, sprint_id: int, member_name: str,
                           available_capacity: int, leaves_planned: int = 0):
        """Set sprint capacity for a team member"""
        capacity = SprintCapacity(
            sprint_session_id=sprint_id,
            member_name=member_name,
            available_capacity=available_capacity,
            leaves_planned=leaves_planned,
            availability_percentage=((available_capacity - leaves_planned * 8) / available_capacity * 100)
            if available_capacity > 0 else 0
        )
        self.session.add(capacity)
        self.session.commit()
        return capacity
    
    def get_sprint_capacity(self, sprint_id: int):
        """Get sprint capacity for all team members"""
        return self.session.query(SprintCapacity).filter(
            SprintCapacity.sprint_session_id == sprint_id
        ).all()
    
    # ========== DEPENDENCIES ==========
    
    def create_dependency(self, story_id: int, depends_on_story_id: str,
                         dependency_type: str = "blocks", description: str = ""):
        """Create a story dependency"""
        dependency = Dependency(
            story_id=story_id,
            depends_on_story_id=depends_on_story_id,
            dependency_type=dependency_type,
            description=description,
            status="active"
        )
        self.session.add(dependency)
        self.session.commit()
        return dependency
    
    def get_story_dependencies(self, story_id: int):
        """Get all dependencies for a story"""
        return self.session.query(Dependency).filter(
            Dependency.story_id == story_id
        ).all()