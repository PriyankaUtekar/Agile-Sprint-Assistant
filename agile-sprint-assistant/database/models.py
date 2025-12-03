"""
Enhanced Database Models with Full Sprint Tracking
This defines what data we store in our database
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Create base class for all models
Base = declarative_base()

# Database path
DATABASE_PATH = 'sqlite:///database/agile_assistant.db'

# Create engine (initialized at module level for imports)
engine = create_engine(DATABASE_PATH, echo=False)


class SprintSession(Base):
    """
    Main sprint session - stores all sprint information
    """
    __tablename__ = 'sprint_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(200), unique=True, nullable=False)
    team_name = Column(String(100), nullable=False)
    sprint_number = Column(Integer, nullable=False)
    
    # Sprint dates
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    sprint_goal = Column(Text)
    status = Column(String(50), default='planning')  # planning, active, completed
    
    # Capacity and velocity
    total_capacity = Column(Integer, default=0)
    remaining_capacity = Column(Integer, default=0)
    planned_points = Column(Integer, default=0)
    completed_points = Column(Integer, default=0)
    
    # Full state stored as JSON
    state = Column(JSON, nullable=False)
    
    # Approval workflow
    scrum_master_approved = Column(Boolean, default=False)
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships to other tables
    user_stories = relationship("UserStory", back_populates="sprint", cascade="all, delete-orphan")
    daily_standups = relationship("DailyStandup", back_populates="sprint", cascade="all, delete-orphan")
    burndown_data = relationship("BurndownData", back_populates="sprint", cascade="all, delete-orphan")


class UserStory(Base):
    """
    Individual user stories within a sprint
    """
    __tablename__ = 'user_stories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sprint_id = Column(Integer, ForeignKey('sprint_sessions.id'))
    
    story_id = Column(String(50), unique=True, nullable=False)  # US-001
    title = Column(String(300), nullable=False)
    description = Column(Text)
    acceptance_criteria = Column(Text)
    
    # Story points and estimation
    story_points = Column(Integer)
    estimated_hours = Column(Float)
    story_points_approved = Column(Boolean, default=False)
    
    # Assignment
    assigned_to = Column(String(100))
    
    # Status
    status = Column(String(50), default='planned')  # planned, in_progress, in_review, done
    
    # Priority and type
    priority = Column(String(20))  # high, medium, low
    story_type = Column(String(50))  # feature, bug, technical_debt, defect
    
    # Dates
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sprint = relationship("SprintSession", back_populates="user_stories")
    dependencies = relationship("Dependency", foreign_keys="Dependency.story_id", back_populates="story")
    risks = relationship("Risk", back_populates="story")
    issues = relationship("Issue", back_populates="story")


class TeamMember(Base):
    """
    Team members and their capacity
    """
    __tablename__ = 'team_members'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50))  # developer, tester, designer
    email = Column(String(100))
    
    # Default capacity per sprint
    default_capacity = Column(Integer, default=8)
    
    # Skills as JSON array
    skills = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SprintCapacity(Base):
    """
    Individual team member capacity for each sprint
    """
    __tablename__ = 'sprint_capacity'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sprint_session_id = Column(Integer, ForeignKey('sprint_sessions.id'))
    member_name = Column(String(100), nullable=False)
    
    available_capacity = Column(Integer)
    allocated_capacity = Column(Integer, default=0)
    
    leaves_planned = Column(Integer, default=0)
    availability_percentage = Column(Float, default=100.0)
    
    notes = Column(Text)


class Dependency(Base):
    """
    Dependencies between user stories
    """
    __tablename__ = 'dependencies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(Integer, ForeignKey('user_stories.id'))
    depends_on_story_id = Column(String(50))
    
    dependency_type = Column(String(50))  # blocks, requires, related_to
    description = Column(Text)
    status = Column(String(50), default='active')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    story = relationship("UserStory", foreign_keys=[story_id], back_populates="dependencies")


class Risk(Base):
    """
    Risks associated with sprint or stories
    """
    __tablename__ = 'risks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sprint_session_id = Column(Integer, ForeignKey('sprint_sessions.id'))
    story_id = Column(Integer, ForeignKey('user_stories.id'), nullable=True)
    
    risk_id = Column(String(50), unique=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    
    probability = Column(String(20))  # high, medium, low
    impact = Column(String(20))  # high, medium, low
    severity = Column(String(20))  # critical, high, medium, low
    
    mitigation_plan = Column(Text)
    owner = Column(String(100))
    status = Column(String(50), default='open')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    story = relationship("UserStory", back_populates="risks")


class Issue(Base):
    """
    Issues and blockers
    """
    __tablename__ = 'issues'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sprint_session_id = Column(Integer, ForeignKey('sprint_sessions.id'))
    story_id = Column(Integer, ForeignKey('user_stories.id'), nullable=True)
    
    issue_id = Column(String(50), unique=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    
    issue_type = Column(String(50))  # blocker, impediment, defect
    severity = Column(String(20))
    
    reported_by = Column(String(100))
    assigned_to = Column(String(100))
    status = Column(String(50), default='open')
    
    resolution = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    story = relationship("UserStory", back_populates="issues")


class DailyStandup(Base):
    """
    Daily standup updates
    """
    __tablename__ = 'daily_standups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sprint_id = Column(Integer, ForeignKey('sprint_sessions.id'))
    
    standup_date = Column(DateTime, nullable=False)
    member_name = Column(String(100), nullable=False)
    
    yesterday = Column(Text)
    today = Column(Text)
    blockers = Column(Text)
    
    hours_worked = Column(Float)
    story_ids_worked_on = Column(JSON)
    confidence_level = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sprint = relationship("SprintSession", back_populates="daily_standups")


class BurndownData(Base):
    """
    Burndown chart data points
    """
    __tablename__ = 'burndown_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sprint_id = Column(Integer, ForeignKey('sprint_sessions.id'))
    
    date = Column(DateTime, nullable=False)
    
    remaining_points = Column(Integer)
    completed_points = Column(Integer)
    ideal_remaining = Column(Float)
    
    stories_completed = Column(Integer, default=0)
    stories_in_progress = Column(Integer, default=0)
    stories_blocked = Column(Integer, default=0)
    
    daily_velocity = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sprint = relationship("SprintSession", back_populates="burndown_data")


class TeamMemory(Base):
    """
    Long-term team memory and learnings
    """
    __tablename__ = 'team_memory'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String(100), nullable=False)
    
    memory_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    
    sprint_number = Column(Integer)
    relevance_score = Column(Integer, default=50)
    
    tags = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Retrospective(Base):
    """
    Sprint retrospective sessions
    """
    __tablename__ = 'retrospectives'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sprint_session_id = Column(Integer, ForeignKey('sprint_sessions.id'))
    
    retro_date = Column(DateTime, default=datetime.utcnow)
    facilitator = Column(String(100))
    
    # What went well
    what_went_well = Column(JSON)
    
    # What didn't go well
    what_didnt_go_well = Column(JSON)
    
    # What to improve
    what_to_improve = Column(JSON)
    
    # Overall summary
    summary = Column(Text)
    
    # Team sentiment (1-10)
    team_sentiment = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    action_items = relationship("ActionItem", back_populates="retrospective", cascade="all, delete-orphan")


class ActionItem(Base):
    """
    Action items from retrospectives
    """
    __tablename__ = 'action_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    retrospective_id = Column(Integer, ForeignKey('retrospectives.id'))
    
    action_id = Column(String(50), unique=True)  # AI-001
    title = Column(String(300), nullable=False)
    description = Column(Text)
    
    assigned_to = Column(String(100))
    target_date = Column(DateTime)
    
    priority = Column(String(20))  # high, medium, low
    status = Column(String(50), default='open')  # open, in_progress, completed, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    retrospective = relationship("Retrospective", back_populates="action_items")


class StoryEstimation(Base):
    """
    Track story estimations - team vs agent
    """
    __tablename__ = 'story_estimations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(Integer, ForeignKey('user_stories.id'))
    
    team_estimate = Column(Integer)  # Team's estimate
    agent_estimate = Column(Integer)  # Agent's estimate
    final_estimate = Column(Integer)  # Final approved estimate
    
    team_reasoning = Column(Text)
    agent_reasoning = Column(Text)
    
    team_approved_agent = Column(Boolean, default=False)  # Did team accept agent's estimate?
    
    estimated_by = Column(String(100))
    estimated_at = Column(DateTime, default=datetime.utcnow)


# Initialize database
def init_database():
    """Create database and all tables"""
    # Create database folder if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("Database initialized successfully!")
    return engine


# Create session factory
def get_session_factory():
    """Get database session factory"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


# Initialize on import
if __name__ == "__main__":
    init_database()
    print("All database models created!")