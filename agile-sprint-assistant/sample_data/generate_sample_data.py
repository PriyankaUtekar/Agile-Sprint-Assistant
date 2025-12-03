"""
Generate sample data for 3 sprints
- Sprint 1 & 2: Completed
- Sprint 3: In Planning

This script clears existing data before inserting new sample data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import (
    SprintSession, UserStory, TeamMember, SprintCapacity,
    Dependency, Risk, Issue, DailyStandup, BurndownData, TeamMemory,
    get_session_factory, init_database
)
from datetime import datetime, timedelta
import json

# Initialize database
init_database()
SessionLocal = get_session_factory()
db = SessionLocal()

print("🧹 Clearing existing data...")

# Clear existing data in correct order (respecting foreign keys)
try:
    db.query(BurndownData).delete()
    db.query(DailyStandup).delete()
    db.query(Dependency).delete()
    db.query(Risk).delete()
    db.query(Issue).delete()
    db.query(SprintCapacity).delete()
    db.query(UserStory).delete()
    db.query(TeamMemory).delete()
    db.query(TeamMember).delete()
    db.query(SprintSession).delete()
    
    # Try to clear these if they exist
    try:
        from database.models import Retrospective, ActionItem, StoryEstimation
        db.query(ActionItem).delete()
        db.query(Retrospective).delete()
        db.query(StoryEstimation).delete()
    except ImportError:
        pass  # Models don't exist yet
    
    db.commit()
    print("✅ Existing data cleared\n")
except Exception as e:
    db.rollback()
    print(f"⚠️ Warning during cleanup: {e}\n")

print("🎨 Generating sample data for Alpha Team...\n")

# ========== TEAM MEMBERS ==========
print("👥 Creating team members...")

team_members_data = [
    {"name": "Sarah Chen", "role": "Senior Developer", "email": "sarah.chen@company.com", "capacity": 10, "skills": ["Python", "React", "API Design"]},
    {"name": "Mike Johnson", "role": "Full Stack Developer", "email": "mike.johnson@company.com", "capacity": 8, "skills": ["JavaScript", "Node.js", "MongoDB"]},
    {"name": "Priya Sharma", "role": "Frontend Developer", "email": "priya.sharma@company.com", "capacity": 9, "skills": ["React", "CSS", "UI/UX"]},
    {"name": "David Kim", "role": "Backend Developer", "email": "david.kim@company.com", "capacity": 8, "skills": ["Java", "Spring Boot", "PostgreSQL"]},
    {"name": "Emily Rodriguez", "role": "QA Engineer", "email": "emily.rodriguez@company.com", "capacity": 7, "skills": ["Testing", "Automation", "Selenium"]},
]

for member_data in team_members_data:
    member = TeamMember(
        name=member_data["name"],
        role=member_data["role"],
        email=member_data["email"],
        default_capacity=member_data["capacity"],
        skills=member_data["skills"]
    )
    db.add(member)

db.commit()
print(f"✅ Created {len(team_members_data)} team members\n")

# ========== SPRINT 1 (COMPLETED) ==========
print("📅 Creating Sprint 1 (Completed)...")

sprint1_start = datetime.now() - timedelta(days=42)
sprint1_end = datetime.now() - timedelta(days=28)

sprint1 = SprintSession(
    session_id="AlphaTeam_Sprint_1",
    team_name="Alpha Team",
    sprint_number=1,
    start_date=sprint1_start,
    end_date=sprint1_end,
    sprint_goal="Implement user authentication and profile management",
    status="completed",
    total_capacity=42,
    remaining_capacity=0,
    planned_points=40,
    completed_points=38,
    scrum_master_approved=True,
    approved_by="John Smith (Scrum Master)",
    approved_at=sprint1_start,
    state={
        "team_name": "Alpha Team",
        "sprint_number": 1,
        "sprint_goals": ["User authentication", "Profile management", "Security implementation"],
        "velocity": 38,
        "team_satisfaction": 85
    }
)
db.add(sprint1)
db.commit()

# Sprint 1 User Stories
sprint1_stories = [
    {
        "story_id": "US-001",
        "title": "User Registration",
        "description": "As a new user, I want to register an account so that I can access the platform",
        "acceptance_criteria": "User can register with email and password, receives confirmation email",
        "story_points": 5,
        "assigned_to": "Sarah Chen",
        "status": "done",
        "priority": "high",
        "story_type": "feature",
        "completed_at": sprint1_start + timedelta(days=3)
    },
    {
        "story_id": "US-002",
        "title": "User Login",
        "description": "As a registered user, I want to login so that I can access my account",
        "acceptance_criteria": "User can login with credentials, session management implemented",
        "story_points": 5,
        "assigned_to": "Mike Johnson",
        "status": "done",
        "priority": "high",
        "story_type": "feature",
        "completed_at": sprint1_start + timedelta(days=4)
    },
    {
        "story_id": "US-003",
        "title": "Password Reset",
        "description": "As a user, I want to reset my password if I forget it",
        "acceptance_criteria": "Email-based password reset flow implemented",
        "story_points": 8,
        "assigned_to": "Sarah Chen",
        "status": "done",
        "priority": "medium",
        "story_type": "feature",
        "completed_at": sprint1_start + timedelta(days=7)
    },
    {
        "story_id": "US-004",
        "title": "User Profile Page",
        "description": "As a user, I want to view and edit my profile information",
        "acceptance_criteria": "Profile page displays user info, allows editing",
        "story_points": 5,
        "assigned_to": "Priya Sharma",
        "status": "done",
        "priority": "medium",
        "story_type": "feature",
        "completed_at": sprint1_start + timedelta(days=8)
    },
    {
        "story_id": "US-005",
        "title": "Profile Picture Upload",
        "description": "As a user, I want to upload a profile picture",
        "acceptance_criteria": "Image upload, cropping, and storage implemented",
        "story_points": 5,
        "assigned_to": "David Kim",
        "status": "done",
        "priority": "low",
        "story_type": "feature",
        "completed_at": sprint1_start + timedelta(days=10)
    },
    {
        "story_id": "US-006",
        "title": "Security Audit",
        "description": "As a developer, I need to perform security audit on auth system",
        "acceptance_criteria": "Security review completed, vulnerabilities addressed",
        "story_points": 8,
        "assigned_to": "Emily Rodriguez",
        "status": "done",
        "priority": "high",
        "story_type": "technical_debt",
        "completed_at": sprint1_start + timedelta(days=12)
    },
    {
        "story_id": "US-007",
        "title": "Session Management",
        "description": "As a user, I want my session to be secure and manageable",
        "acceptance_criteria": "Token-based auth, session timeout implemented",
        "story_points": 2,
        "assigned_to": "Mike Johnson",
        "status": "in_progress",
        "priority": "medium",
        "story_type": "feature"
    }
]

for story_data in sprint1_stories:
    story = UserStory(
        sprint_id=sprint1.id,
        story_id=story_data["story_id"],
        title=story_data["title"],
        description=story_data["description"],
        acceptance_criteria=story_data["acceptance_criteria"],
        story_points=story_data["story_points"],
        story_points_approved=True,
        assigned_to=story_data["assigned_to"],
        status=story_data["status"],
        priority=story_data["priority"],
        story_type=story_data["story_type"],
        started_at=sprint1_start + timedelta(days=1),
        completed_at=story_data.get("completed_at")
    )
    db.add(story)

db.commit()
print(f"✅ Created {len(sprint1_stories)} user stories for Sprint 1\n")

# Sprint 1 Burndown Data
print("📊 Creating burndown data for Sprint 1...")
sprint1_days = 14
total_points = 40
for day in range(sprint1_days + 1):
    date = sprint1_start + timedelta(days=day)
    ideal_remaining = total_points * (1 - day / sprint1_days)
    
    # Actual burndown (slightly better than ideal)
    if day < 3:
        actual_remaining = total_points
    elif day < 7:
        actual_remaining = total_points - (day * 3)
    elif day < 12:
        actual_remaining = total_points - (day * 3.5)
    else:
        actual_remaining = 2 if day < 14 else 0
    
    burndown = BurndownData(
        sprint_id=sprint1.id,
        date=date,
        remaining_points=int(max(0, actual_remaining)),
        completed_points=total_points - int(max(0, actual_remaining)),
        ideal_remaining=ideal_remaining,
        stories_completed=min(day * 0.5, 6),
        stories_in_progress=1 if day < 13 else 0,
        stories_blocked=0,
        daily_velocity=3.0 if day > 2 else 0
    )
    db.add(burndown)

db.commit()
print("✅ Burndown data created for Sprint 1\n")

# ========== SPRINT 2 (COMPLETED) ==========
print("📅 Creating Sprint 2 (Completed)...")

sprint2_start = datetime.now() - timedelta(days=28)
sprint2_end = datetime.now() - timedelta(days=14)

sprint2 = SprintSession(
    session_id="AlphaTeam_Sprint_2",
    team_name="Alpha Team",
    sprint_number=2,
    start_date=sprint2_start,
    end_date=sprint2_end,
    sprint_goal="Build dashboard and implement data visualization",
    status="completed",
    total_capacity=42,
    remaining_capacity=0,
    planned_points=42,
    completed_points=40,
    scrum_master_approved=True,
    approved_by="John Smith (Scrum Master)",
    approved_at=sprint2_start,
    state={
        "team_name": "Alpha Team",
        "sprint_number": 2,
        "sprint_goals": ["Dashboard implementation", "Data visualization", "API integration"],
        "velocity": 40,
        "team_satisfaction": 88
    }
)
db.add(sprint2)
db.commit()

# Sprint 2 User Stories
sprint2_stories = [
    {
        "story_id": "US-008",
        "title": "Dashboard Layout",
        "description": "As a user, I want to see a dashboard when I login",
        "acceptance_criteria": "Responsive dashboard layout with navigation",
        "story_points": 5,
        "assigned_to": "Priya Sharma",
        "status": "done",
        "priority": "high",
        "story_type": "feature",
        "completed_at": sprint2_start + timedelta(days=4)
    },
    {
        "story_id": "US-009",
        "title": "Data Analytics API",
        "description": "As a system, I need an API to fetch analytics data",
        "acceptance_criteria": "RESTful API endpoints for analytics data",
        "story_points": 8,
        "assigned_to": "David Kim",
        "status": "done",
        "priority": "high",
        "story_type": "feature",
        "completed_at": sprint2_start + timedelta(days=6)
    },
    {
        "story_id": "US-010",
        "title": "Chart Components",
        "description": "As a user, I want to see data visualized in charts",
        "acceptance_criteria": "Bar, line, and pie charts implemented",
        "story_points": 8,
        "assigned_to": "Priya Sharma",
        "status": "done",
        "priority": "high",
        "story_type": "feature",
        "completed_at": sprint2_start + timedelta(days=8)
    },
    {
        "story_id": "US-011",
        "title": "Real-time Updates",
        "description": "As a user, I want dashboard to update in real-time",
        "acceptance_criteria": "WebSocket connection, automatic refresh",
        "story_points": 13,
        "assigned_to": "Mike Johnson",
        "status": "done",
        "priority": "medium",
        "story_type": "feature",
        "completed_at": sprint2_start + timedelta(days=12)
    },
    {
        "story_id": "US-012",
        "title": "Export Dashboard Data",
        "description": "As a user, I want to export dashboard data to CSV",
        "acceptance_criteria": "Export functionality for all charts",
        "story_points": 3,
        "assigned_to": "Sarah Chen",
        "status": "done",
        "priority": "low",
        "story_type": "feature",
        "completed_at": sprint2_start + timedelta(days=10)
    },
    {
        "story_id": "US-013",
        "title": "Performance Optimization",
        "description": "As a developer, I need to optimize dashboard loading",
        "acceptance_criteria": "Page load time under 2 seconds",
        "story_points": 3,
        "assigned_to": "Mike Johnson",
        "status": "done",
        "priority": "medium",
        "story_type": "technical_debt",
        "completed_at": sprint2_start + timedelta(days=11)
    },
    {
        "story_id": "US-014",
        "title": "Fix Chart Rendering Bug",
        "description": "Charts not rendering correctly on mobile devices",
        "acceptance_criteria": "Charts display correctly on all screen sizes",
        "story_points": 2,
        "assigned_to": "Priya Sharma",
        "status": "in_progress",
        "priority": "high",
        "story_type": "defect"
    }
]

for story_data in sprint2_stories:
    story = UserStory(
        sprint_id=sprint2.id,
        story_id=story_data["story_id"],
        title=story_data["title"],
        description=story_data["description"],
        acceptance_criteria=story_data["acceptance_criteria"],
        story_points=story_data["story_points"],
        story_points_approved=True,
        assigned_to=story_data["assigned_to"],
        status=story_data["status"],
        priority=story_data["priority"],
        story_type=story_data["story_type"],
        started_at=sprint2_start + timedelta(days=1),
        completed_at=story_data.get("completed_at")
    )
    db.add(story)

db.commit()
print(f"✅ Created {len(sprint2_stories)} user stories for Sprint 2\n")

# Sprint 2 Issues
print("⚠️  Creating issues for Sprint 2...")
sprint2_issues = [
    {
        "issue_id": "I-001",
        "title": "Chart library compatibility issue",
        "description": "Chart.js conflicting with other dependencies",
        "issue_type": "blocker",
        "severity": "high",
        "reported_by": "Priya Sharma",
        "assigned_to": "Mike Johnson",
        "status": "resolved",
        "resolution": "Upgraded to Chart.js v4",
        "resolved_at": sprint2_start + timedelta(days=5)
    }
]

for issue_data in sprint2_issues:
    issue = Issue(
        sprint_session_id=sprint2.id,
        issue_id=issue_data["issue_id"],
        title=issue_data["title"],
        description=issue_data["description"],
        issue_type=issue_data["issue_type"],
        severity=issue_data["severity"],
        reported_by=issue_data["reported_by"],
        assigned_to=issue_data["assigned_to"],
        status=issue_data["status"],
        resolution=issue_data.get("resolution"),
        resolved_at=issue_data.get("resolved_at")
    )
    db.add(issue)

db.commit()
print("✅ Issues created for Sprint 2\n")

# Sprint 2 Burndown
print("📊 Creating burndown data for Sprint 2...")
total_points_s2 = 42
for day in range(15):
    date = sprint2_start + timedelta(days=day)
    ideal_remaining = total_points_s2 * (1 - day / 14)
    
    if day < 4:
        actual_remaining = total_points_s2
    elif day < 8:
        actual_remaining = total_points_s2 - (day * 3.5)
    elif day < 13:
        actual_remaining = total_points_s2 - (day * 3.2)
    else:
        actual_remaining = 2 if day < 14 else 0
    
    burndown = BurndownData(
        sprint_id=sprint2.id,
        date=date,
        remaining_points=int(max(0, actual_remaining)),
        completed_points=total_points_s2 - int(max(0, actual_remaining)),
        ideal_remaining=ideal_remaining,
        stories_completed=min(day * 0.5, 6),
        stories_in_progress=1,
        stories_blocked=1 if 3 <= day <= 5 else 0,
        daily_velocity=3.2
    )
    db.add(burndown)

db.commit()
print("✅ Burndown data created for Sprint 2\n")

# ========== SPRINT 3 (IN PLANNING) ==========
print("📅 Creating Sprint 3 (In Planning)...")

sprint3_start = datetime.now()
sprint3_end = datetime.now() + timedelta(days=14)

sprint3 = SprintSession(
    session_id="AlphaTeam_Sprint_3",
    team_name="Alpha Team",
    sprint_number=3,
    start_date=sprint3_start,
    end_date=sprint3_end,
    sprint_goal="Implement notification system and user preferences",
    status="planning",
    total_capacity=40,  # Reduced due to one team member on leave
    remaining_capacity=40,
    planned_points=0,  # Not yet planned
    completed_points=0,
    scrum_master_approved=False,
    state={
        "team_name": "Alpha Team",
        "sprint_number": 3,
        "sprint_goals": ["Notification system", "User preferences", "Email integration"],
        "previous_velocity": 40,
        "team_satisfaction": None
    }
)
db.add(sprint3)
db.commit()

# Sprint 3 Capacity (Emily on leave for 2 days)
sprint3_capacity = [
    {"member": "Sarah Chen", "capacity": 10, "availability": 100},
    {"member": "Mike Johnson", "capacity": 8, "availability": 100},
    {"member": "Priya Sharma", "capacity": 9, "availability": 100},
    {"member": "David Kim", "capacity": 8, "availability": 100},
    {"member": "Emily Rodriguez", "capacity": 5, "availability": 71, "leaves": 2},  # 2 days off
]

for cap_data in sprint3_capacity:
    capacity = SprintCapacity(
        sprint_session_id=sprint3.id,
        member_name=cap_data["member"],
        available_capacity=cap_data["capacity"],
        leaves_planned=cap_data.get("leaves", 0),
        availability_percentage=cap_data["availability"]
    )
    db.add(capacity)

db.commit()

# Sprint 3 User Stories (NOT YET APPROVED - NO STORY POINTS)
sprint3_stories = [
    {
        "story_id": "US-015",
        "title": "In-App Notifications",
        "description": "As a user, I want to receive in-app notifications for important events",
        "acceptance_criteria": "Real-time notification system with badge counts",
        "story_points": None,  # No points until estimated and approved
        "assigned_to": None,
        "status": "planned",
        "priority": "high",
        "story_type": "feature",
        "story_points_approved": False
    },
    {
        "story_id": "US-016",
        "title": "Email Notifications",
        "description": "As a user, I want to receive email notifications",
        "acceptance_criteria": "Email service integration, templated emails",
        "story_points": None,  # No points until estimated and approved
        "assigned_to": None,
        "status": "planned",
        "priority": "high",
        "story_type": "feature",
        "story_points_approved": False
    },
    {
        "story_id": "US-017",
        "title": "Notification Preferences",
        "description": "As a user, I want to control which notifications I receive",
        "acceptance_criteria": "Settings page for notification preferences",
        "story_points": None,  # No points until estimated and approved
        "assigned_to": None,
        "status": "planned",
        "priority": "medium",
        "story_type": "feature",
        "story_points_approved": False
    },
    {
        "story_id": "US-018",
        "title": "Push Notifications",
        "description": "As a user, I want to receive push notifications on mobile",
        "acceptance_criteria": "PWA push notification support",
        "story_points": None,  # No points until estimated and approved
        "assigned_to": None,
        "status": "planned",
        "priority": "medium",
        "story_type": "feature",
        "story_points_approved": False
    },
    {
        "story_id": "US-019",
        "title": "User Theme Preferences",
        "description": "As a user, I want to choose between light and dark mode",
        "acceptance_criteria": "Theme switcher, preference saved",
        "story_points": None,  # No points until estimated and approved
        "assigned_to": None,
        "status": "planned",
        "priority": "low",
        "story_type": "feature",
        "story_points_approved": False
    },
    {
        "story_id": "US-020",
        "title": "Language Preferences",
        "description": "As a user, I want to select my preferred language",
        "acceptance_criteria": "Multi-language support, i18n implemented",
        "story_points": None,  # No points until estimated and approved
        "assigned_to": None,
        "status": "planned",
        "priority": "low",
        "story_type": "feature",
        "story_points_approved": False
    },
    {
        "story_id": "US-021",
        "title": "Notification Service Refactoring",
        "description": "Refactor notification service for better maintainability",
        "acceptance_criteria": "Code refactored, tests passing",
        "story_points": None,  # No points until estimated and approved
        "assigned_to": None,
        "status": "planned",
        "priority": "medium",
        "story_type": "technical_debt",
        "story_points_approved": False
    }
]

for story_data in sprint3_stories:
    story = UserStory(
        sprint_id=sprint3.id,
        story_id=story_data["story_id"],
        title=story_data["title"],
        description=story_data["description"],
        acceptance_criteria=story_data["acceptance_criteria"],
        story_points=story_data["story_points"],
        story_points_approved=story_data["story_points_approved"],
        assigned_to=story_data["assigned_to"],
        status=story_data["status"],
        priority=story_data["priority"],
        story_type=story_data["story_type"]
    )
    db.add(story)

db.commit()
print(f"✅ Created {len(sprint3_stories)} user stories for Sprint 3 (awaiting estimation)\n")

# Sprint 3 Dependencies
print("🔗 Creating dependencies for Sprint 3...")
dependencies = [
    {
        "story_id": "US-016",
        "depends_on": "US-015",
        "type": "requires",
        "description": "Email notifications require base notification system"
    },
    {
        "story_id": "US-017",
        "depends_on": "US-015",
        "type": "requires",
        "description": "Preferences require notification system to be implemented"
    }
]

for dep_data in dependencies:
    # Find the story
    story = db.query(UserStory).filter_by(story_id=dep_data["story_id"]).first()
    if story:
        dependency = Dependency(
            story_id=story.id,
            depends_on_story_id=dep_data["depends_on"],
            dependency_type=dep_data["type"],
            description=dep_data["description"]
        )
        db.add(dependency)

db.commit()
print("✅ Dependencies created for Sprint 3\n")

# Sprint 3 Risks
print("⚠️  Creating risks for Sprint 3...")
risks = [
    {
        "risk_id": "R-001",
        "title": "Email service integration complexity",
        "description": "Integration with email service provider may be complex",
        "probability": "medium",
        "impact": "high",
        "severity": "high",
        "mitigation_plan": "Research email services early, have backup option ready",
        "owner": "David Kim"
    },
    {
        "risk_id": "R-002",
        "title": "Team member on leave",
        "description": "Emily Rodriguez on leave for 2 days, reduced QA capacity",
        "probability": "high",
        "impact": "medium",
        "severity": "medium",
        "mitigation_plan": "Other team members to handle testing during absence",
        "owner": "Sarah Chen"
    }
]

for risk_data in risks:
    risk = Risk(
        sprint_session_id=sprint3.id,
        risk_id=risk_data["risk_id"],
        title=risk_data["title"],
        description=risk_data["description"],
        probability=risk_data["probability"],
        impact=risk_data["impact"],
        severity=risk_data["severity"],
        mitigation_plan=risk_data["mitigation_plan"],
        owner=risk_data["owner"]
    )
    db.add(risk)

db.commit()
print("✅ Risks created for Sprint 3\n")

# ========== TEAM MEMORIES ==========
print("🧠 Creating team memories...")

memories = [
    {
        "team": "Alpha Team",
        "type": "lesson",
        "content": "Daily standups at 9:30 AM work best for the team's schedule",
        "sprint": 1,
        "score": 85,
        "tags": ["standup", "process"]
    },
    {
        "team": "Alpha Team",
        "type": "lesson",
        "content": "Breaking down stories larger than 8 points improves accuracy",
        "sprint": 1,
        "score": 90,
        "tags": ["estimation", "planning"]
    },
    {
        "team": "Alpha Team",
        "type": "pattern",
        "content": "Team velocity stabilizing around 38-40 points per sprint",
        "sprint": 2,
        "score": 95,
        "tags": ["velocity", "metrics"]
    },
    {
        "team": "Alpha Team",
        "type": "retrospective",
        "content": "Code reviews taking too long - implement 24-hour review SLA",
        "sprint": 2,
        "score": 80,
        "tags": ["process", "improvement"]
    },
    {
        "team": "Alpha Team",
        "type": "decision",
        "content": "Decided to use Chart.js for all visualization needs",
        "sprint": 2,
        "score": 75,
        "tags": ["technical", "architecture"]
    }
]

for memory_data in memories:
    memory = TeamMemory(
        team_name=memory_data["team"],
        memory_type=memory_data["type"],
        content=memory_data["content"],
        sprint_number=memory_data["sprint"],
        relevance_score=memory_data["score"],
        tags=memory_data["tags"]
    )
    db.add(memory)

db.commit()
print("✅ Team memories created\n")

# Summary
print("\n" + "="*60)
print("✅ SAMPLE DATA GENERATION COMPLETE!")
print("="*60)
print(f"\n📊 Summary:")
print(f"  - Team Members: 5")
print(f"  - Sprint 1: Completed ({sprint1.completed_points}/{sprint1.planned_points} points)")
print(f"  - Sprint 2: Completed ({sprint2.completed_points}/{sprint2.planned_points} points)")
print(f"  - Sprint 3: In Planning ({len(sprint3_stories)} stories, awaiting estimation)")
print(f"  - Total User Stories: {len(sprint1_stories) + len(sprint2_stories) + len(sprint3_stories)}")
print(f"  - Risks: 2")
print(f"  - Issues: 1 (resolved)")
print(f"  - Dependencies: 2")
print(f"  - Team Memories: {len(memories)}")
print(f"\n🎉 Database ready for testing!\n")

db.close()