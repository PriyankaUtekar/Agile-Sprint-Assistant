# Agile-Sprint-Assistant
AI-powered Agile Sprint Assistant with planning, standups, and retrospectives features

# 🚀 Agile Sprint Assistant

An AI-powered multi-agent system for managing agile sprint ceremonies with intelligent automation, collaborative decision-making, and continuous learning.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Google-Gemini%202.5-orange.svg)](https://ai.google.dev/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Agent Details](#agent-details)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### **The Problem**

Agile teams spend 15-20% of sprint time in meetings and administrative tasks. Story point estimation is often inaccurate, retrospectives are shallow, and insights from past sprints are lost.

### **The Solution**

A multi-agent AI system that:
- ✅ Provides AI-assisted story point estimation
- ✅ Generates focused standup summaries with blocker analysis
- ✅ Extracts actionable insights from retrospectives
- ✅ Maintains team knowledge across sprints
- ✅ Automates meeting documentation and notifications

### **Why Agents?**

Multi-agent architecture allows **specialization** (each agent optimized for specific ceremonies), **collaboration** (agents share insights), and **continuous learning** (system improves with each sprint).

---

## ✨ Features

### **Core Capabilities**

#### **🎯 Sprint Planning**
- AI-powered story point estimation using Google Gemini
- Collaborative human-AI decision making
- Historical velocity analysis
- Capacity planning with team availability
- Sprint plan approval workflow
- Automatic sprint activation

#### **👥 Daily Standups**
- Structured update collection (Yesterday/Today/Blockers)
- AI-generated summaries with pattern detection
- Blocker identification and prioritization
- Confidence level tracking
- Slack notifications for team alignment

#### **🔄 Sprint Retrospectives**
- Multi-category feedback (Went Well/Didn't Go Well/Improve)
- Sentiment analysis (1-10 team mood)
- Action item creation and tracking
- Theme extraction from feedback
- Knowledge base population for future sprints

#### **📊 Reports & Analytics**
- Velocity tracking across sprints
- Burndown charts with ideal vs. actual
- Sprint completion metrics
- Story point accuracy analysis
- Interactive Chart.js visualizations

#### **🔔 Integrations**
- Slack notifications via MCP (Model Context Protocol)
- Real-time team updates
- Summary broadcasts
- Action item alerts

---

## 🏗️ Architecture

### **System Architecture**
```
┌─────────────────────────────────────────────────────────┐
│                   Web Interface Layer                    │
│         (FastAPI + Jinja2 + Bootstrap + Chart.js)       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│                 Agent Orchestration Layer                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────── BaseAgent ──────────────────────┐ │
│  │  - Gemini 2.5 Flash Integration                   │ │
│  │  - Context Management                              │ │
│  │  - Rate Limiting                                   │ │
│  │  - Slack Integration                               │ │
│  └────────────────────┬───────────────────────────────┘ │
│                       │                                  │
│  ┌────────┬───────────┼──────────┬─────────┐           │
│  │        │            │          │         │           │
│  ▼        ▼            ▼          ▼         ▼           │
│ ┌──────┐┌───────┐┌─────────┐┌────────┐┌──────────┐   │
│ │Plan  ││Standup││  Retro  ││Reports ││ Memory   │   │
│ │Agent ││Agent  ││  Agent  ││ Agent  ││ System   │   │
│ └──────┘└───────┘└─────────┘└────────┘└──────────┘   │
│                                                          │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│              Persistence & Integration Layer             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐        ┌──────────────────┐     │
│  │ SQLite Database  │        │   Slack API      │     │
│  │  - Sprints       │        │   (via MCP)      │     │
│  │  - Stories       │        │                  │     │
│  │  - Metrics       │        └──────────────────┘     │
│  │  - Retrospectives│                                  │
│  └──────────────────┘                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### **Agent Communication Flow**
```
User → Web UI → FastAPI Routes → Agent Selection
                                       ↓
                    ┌──────────────────┴────────────────────┐
                    │                                        │
                    ▼                                        ▼
            Gemini Processing                      Context Retrieval
         (Natural Language → Action)          (Historical Data + Memory)
                    │                                        │
                    └──────────────────┬────────────────────┘
                                       ↓
                            Database Persistence
                                       ↓
                         ┌─────────────┴─────────────┐
                         │                           │
                         ▼                           ▼
                 Update Shared Memory        Slack Notification
                         │                           │
                         └───────────┬───────────────┘
                                     ↓
                           Next Agent Access
```

---

## 📋 Prerequisites

### **System Requirements**

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 2GB RAM minimum
- **Storage**: 500MB free space

### **Required Services**

1. **Google Gemini API Key** (Required)
   - Get from: [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Free tier: 60 requests/minute
   - Model: Gemini 2.5 Flash

2. **Slack Workspace** (Optional)
   - For team notifications
   - Bot token with permissions: `chat:write`, `channels:read`

---

## 💻 Installation

### **Step 1: Clone Repository**
```bash
git clone https://github.com/PriyankaUtekar/Agile-Sprint-Assistant.git
cd Agile-Sprint-Assistant
```

### **Step 2: Create Virtual Environment**

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verify activation:**
```bash
# You should see (venv) before your command prompt
(venv) C:\path\to\project>
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Expected packages:**
```
fastapi==0.104.1
uvicorn==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
sqlalchemy==2.0.23
google-generativeai==0.3.2
slack-sdk==3.26.1
python-dotenv==1.0.0
python-dateutil==2.8.2
```

**Verify installation:**
```bash
pip list
```

---

## ⚙️ Configuration

### **Step 1: Create Environment File**
```bash
# Copy the example file
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux
```

### **Step 2: Get Google Gemini API Key**

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click **"Create API Key"**
4. Copy the API key (starts with `AIza...`)

### **Step 3: (Optional) Set Up Slack Integration**

#### **Create Slack App:**

1. Go to [Slack API](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Name: `Agile Sprint Assistant`
4. Select your workspace

#### **Configure Bot Permissions:**

1. Go to **"OAuth & Permissions"**
2. Add **Bot Token Scopes**:
   - `chat:write` - Send messages
   - `channels:read` - View channels
   - `channels:history` - Read channel history
3. Click **"Install to Workspace"**
4. Copy **Bot User OAuth Token** (starts with `xoxb-`)

#### **Get Channel ID:**

1. Open Slack
2. Right-click on channel → **"View channel details"**
3. Scroll down, copy **Channel ID** (starts with `C`)

### **Step 4: Update .env File**

Open `.env` file and add your credentials:
```env
# Google Gemini API Configuration
GOOGLE_API_KEY=AIzaSyA... # YOUR ACTUAL KEY HERE

# Database Configuration
DATABASE_URL=sqlite:///database/agile_assistant.db

# Slack Configuration (Optional)
SLACK_BOT_TOKEN=xoxb-... # YOUR ACTUAL TOKEN HERE
SLACK_CHANNEL_ID=C... # YOUR ACTUAL CHANNEL ID HERE
SLACK_ENABLED=true  # Set to false to disable Slack
```

**⚠️ SECURITY WARNING:**
- Never commit `.env` file to Git
- Never share API keys publicly
- Rotate keys if exposed

---

## 🚀 Usage Guide

### **Step 1: Initialize Database**
```bash
python database/init_db.py
```

**Expected output:**
```
Database initialized successfully!
All database models created!
```

**Optionally, load sample data:**
```bash
python sample_data/load_sample_data.py
```

This creates:
- Sample sprint (Sprint 3)
- Team members (5 developers)
- User stories (10 stories)
- Historical data for testing

### **Step 2: Start the Application**
```bash
cd ui
python app.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### **Step 3: Access Web Interface**

Open browser and navigate to:
```
http://localhost:8001
```

### **Step 4: Navigate the Interface**

#### **Dashboard (Home Page)**
- Overview of current sprint
- Quick stats (velocity, completion rate)
- Navigation to all features

#### **Sprint Planning** (`/planning`)

**Workflow:**

1. **Start Planning Session**
   - Click "Start Planning Session"
   - System loads current sprint data

2. **Estimate Stories**
   - Select user story from dropdown
   - Enter team's story point estimate (1, 2, 3, 5, 8, 13)
   - Provide reasoning
   - Click "Get AI Comparison"

3. **Review AI Estimate**
   - System shows both team and AI estimates
   - AI explains reasoning
   - Choose to accept team estimate or AI estimate
   - Click appropriate button

4. **Generate Sprint Plan**
   - Once all stories estimated
   - Click "Generate Sprint Plan"
   - AI creates comprehensive plan with:
     - Sprint goal summary
     - Capacity analysis
     - Risk identification
     - Recommendations

5. **Approve Plan**
   - Scrum Master enters name
   - Optionally add comments
   - Click "Approve Plan"
   - Sprint automatically activates

#### **Daily Standup** (`/`)

**Workflow:**

1. **Start Standup**
   - Click "Start Daily Standup"
   - System prepares session

2. **Submit Updates** (one per team member)
   - Select team member from dropdown
   - Enter what was completed yesterday
   - Enter plan for today
   - List any blockers (or "None")
   - Click "Submit Update"

3. **Generate Summary**
   - After all team members submit
   - Click "Generate Summary"
   - AI analyzes all updates and creates:
     - Key highlights
     - Blocker analysis with severity
     - Velocity assessment
     - Action items
   - Summary sent to Slack (if enabled)

#### **Retrospective** (`/retrospective`)

**Workflow:**

1. **Start Retrospective**
   - Select completed sprint from dropdown
   - Enter facilitator name
   - Click "Start Retrospective"

2. **Collect Feedback**
   - Select category:
     - ✅ What Went Well
     - ❌ What Didn't Go Well
     - ➡️ What Can We Improve
   - Enter feedback text
   - Enter your name
   - Click "Submit Feedback"
   - Repeat for all team members

3. **Set Team Sentiment**
   - Rate overall team mood (1-10 scale)
   - Click "Set Team Sentiment"

4. **Create Action Items**
   - Click "Add Action Item" button
   - For each action:
     - Enter title
     - Enter description (optional)
     - Assign to team member
     - Set priority (High/Medium/Low)
     - Set target date (optional)
   - Click "Create Action Items"

5. **Generate Summary**
   - Click "Generate Summary"
   - AI creates comprehensive retrospective report:
     - Executive summary
     - Detailed analysis of feedback
     - Pattern identification
     - Action items review
     - Key takeaways
     - Recommendations for next sprint
   - Summary stored in database
   - Notifications sent to Slack

#### **Reports** (`/reports`)

**Available Reports:**

1. **Sprint Selection**
   - Dropdown to select any past sprint

2. **Velocity Chart**
   - Bar chart showing planned vs. completed points
   - Trend line across sprints
   - Velocity average

3. **Burndown Chart**
   - Line chart of remaining points over sprint
   - Ideal burndown line (reference)
   - Actual burndown line
   - Shows if team is on track

4. **Sprint Metrics**
   - **For Planning/Active Sprints:**
     - Total stories
     - Estimated stories
     - Planned story points
     - Total team capacity
   - **For Completed Sprints:**
     - Planned points
     - Completed points
     - Completion rate (%)
     - Total capacity used

---

## 🤖 Agent Details

### **1. BaseAgent**

**Purpose**: Shared foundation for all specialized agents

**Capabilities:**
- Gemini API integration with rate limiting
- Context management (maintains conversation history)
- Slack notification system
- Session tracking
- Error handling and retry logic

**Key Methods:**
```python
def generate_response(prompt: str) -> str
    # Calls Gemini API with retry logic
    
def add_context(role: str, content: str)
    # Adds message to conversation history
    
def extract_sprint_number(session_id: str) -> int
    # Parses sprint number from session ID
```

### **2. PlanningAgent**

**Purpose**: Intelligent sprint planning assistance

**Workflow:**
```
User submits story → Team provides estimate → Agent analyzes:
  - Story description & acceptance criteria
  - Team's estimate and reasoning
  - Historical velocity
  - Similar past stories
  - Team capacity
→ Agent provides estimate with explanation
→ Team decides (accept AI or use team estimate)
→ All estimates finalized → Generate comprehensive plan
```

**Key Features:**
- Collaborative estimation (human-AI)
- Historical pattern analysis
- Capacity-aware recommendations
- Risk identification
- Approval workflow with sprint activation

**Prompts:**
```python
# Estimation prompt includes:
- Story details
- Team estimate + reasoning
- Historical similar stories
- Team velocity trends
- Current sprint capacity

# Plan generation prompt includes:
- All finalized estimates
- Team capacity breakdown
- Sprint goal
- Historical completion rates
```

### **3. StandupAgent**

**Purpose**: Efficient daily standup management

**Workflow:**
```
Start standup → Collect updates (Yesterday/Today/Blockers)
→ Agent analyzes:
  - Work patterns
  - Blocker severity
  - Team velocity
  - Confidence levels
→ Generate summary with actionable insights
→ Send to Slack
```

**Key Features:**
- Structured update collection
- Pattern detection (who's blocked, who's stuck)
- Blocker categorization by severity
- Velocity tracking
- Confidence assessment

**Analysis:**
- NLP to identify blocker keywords
- Sentiment analysis on confidence
- Workload distribution check
- Cross-team dependency detection

### **4. RetrospectiveAgent**

**Purpose**: Deep insights from sprint retrospectives

**Workflow:**
```
Start retro → Collect feedback (3 categories)
→ Set team sentiment → Create action items
→ Agent analyzes:
  - Feedback themes
  - Sentiment trends
  - Recurring issues
  - Success patterns
→ Generate comprehensive summary
→ Store in knowledge base
```

**Key Features:**
- Multi-category feedback collection
- Sentiment tracking (team mood)
- Theme extraction using NLP
- Action item generation and tracking
- Knowledge base population

**Analysis:**
- Theme clustering (similar feedback grouped)
- Sentiment trend over sprints
- Action item effectiveness tracking
- Pattern identification (recurring problems)

### **5. Memory System**

**Purpose**: Long-term team knowledge retention

**Components:**

1. **Sprint History**
   - All past sprints, stories, estimates
   - Actual vs. estimated completion times
   - Velocity trends

2. **Team Memory**
   - Learnings from retrospectives
   - Best practices discovered
   - Pitfalls to avoid
   - Team preferences

3. **Context Retrieval**
   - Agents query relevant history
   - Similarity-based retrieval
   - Recency-weighted relevance

**Usage:**
```python
# Planning agent retrieves similar stories
historical_stories = db.get_similar_stories(
    title=current_story.title,
    description=current_story.description,
    limit=5
)

# Retrospective agent stores learnings
db.store_team_memory(
    team_name="Alpha Team",
    memory_type="retrospective_learning",
    content="Daily code reviews reduce bugs by 40%",
    relevance_score=95
)
```

---

## 📊 Database Schema

### **Core Tables**

#### **sprint_sessions**
Primary table for sprint tracking
```sql
CREATE TABLE sprint_sessions (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(200) UNIQUE,  -- e.g., "AlphaTeam_Sprint_3"
    team_name VARCHAR(100),
    sprint_number INTEGER,
    start_date DATETIME,
    end_date DATETIME,
    sprint_goal TEXT,
    status VARCHAR(50),  -- planning, active, completed
    total_capacity INTEGER,
    remaining_capacity INTEGER,
    planned_points INTEGER,
    completed_points INTEGER,
    scrum_master_approved BOOLEAN,
    approved_by VARCHAR(100),
    approved_at DATETIME,
    created_at DATETIME,
    updated_at DATETIME
);
```

#### **user_stories**
Individual story tracking
```sql
CREATE TABLE user_stories (
    id INTEGER PRIMARY KEY,
    sprint_id INTEGER FOREIGN KEY,
    story_id VARCHAR(50) UNIQUE,  -- e.g., "US-015"
    title VARCHAR(300),
    description TEXT,
    acceptance_criteria TEXT,
    story_points INTEGER,
    estimated_hours FLOAT,
    story_points_approved BOOLEAN,
    assigned_to VARCHAR(100),
    status VARCHAR(50),  -- planned, in_progress, in_review, done
    priority VARCHAR(20),  -- high, medium, low
    story_type VARCHAR(50),  -- feature, bug, technical_debt
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME
);
```

#### **team_members**
Team roster and capacity
```sql
CREATE TABLE team_members (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(50),  -- developer, tester, designer
    email VARCHAR(100),
    default_capacity INTEGER,  -- story points per sprint
    skills JSON,  -- ["Python", "React", "Testing"]
    created_at DATETIME
);
```

#### **daily_standups**
Standup update history
```sql
CREATE TABLE daily_standups (
    id INTEGER PRIMARY KEY,
    sprint_id INTEGER FOREIGN KEY,
    standup_date DATETIME,
    member_name VARCHAR(100),
    yesterday TEXT,
    today TEXT,
    blockers TEXT,
    hours_worked FLOAT,
    story_ids_worked_on JSON,
    confidence_level VARCHAR(20),  -- high, medium, low
    created_at DATETIME
);
```

#### **retrospectives**
Retrospective sessions
```sql
CREATE TABLE retrospectives (
    id INTEGER PRIMARY KEY,
    sprint_session_id INTEGER FOREIGN KEY,
    retro_date DATETIME,
    facilitator VARCHAR(100),
    what_went_well JSON,  -- array of feedback objects
    what_didnt_go_well JSON,
    what_to_improve JSON,
    summary TEXT,
    team_sentiment INTEGER,  -- 1-10 scale
    created_at DATETIME
);
```

#### **action_items**
Retrospective action items
```sql
CREATE TABLE action_items (
    id INTEGER PRIMARY KEY,
    retrospective_id INTEGER FOREIGN KEY,
    action_id VARCHAR(50),  -- e.g., "AI-003-01"
    title VARCHAR(300),
    description TEXT,
    assigned_to VARCHAR(100),
    target_date DATETIME,
    priority VARCHAR(20),
    status VARCHAR(50),  -- open, in_progress, completed, cancelled
    created_at DATETIME,
    completed_at DATETIME
);
```

#### **burndown_data**
Daily burndown tracking
```sql
CREATE TABLE burndown_data (
    id INTEGER PRIMARY KEY,
    sprint_id INTEGER FOREIGN KEY,
    date DATETIME,
    remaining_points INTEGER,
    completed_points INTEGER,
    ideal_remaining FLOAT,
    stories_completed INTEGER,
    stories_in_progress INTEGER,
    stories_blocked INTEGER,
    daily_velocity FLOAT,
    created_at DATETIME
);
```

#### **team_memory**
Long-term knowledge storage
```sql
CREATE TABLE team_memory (
    id INTEGER PRIMARY KEY,
    team_name VARCHAR(100),
    memory_type VARCHAR(50),  -- retrospective_learning, best_practice, pitfall
    content TEXT,
    sprint_number INTEGER,
    relevance_score INTEGER,  -- 1-100
    tags JSON,
    created_at DATETIME
);
```

### **Relationships**
```
sprint_sessions (1) → (many) user_stories
sprint_sessions (1) → (many) daily_standups
sprint_sessions (1) → (many) burndown_data
sprint_sessions (1) → (1) retrospectives
retrospectives (1) → (many) action_items
```

---

## 🌐 Deployment

### **Local Deployment** (Default)

Already covered in Installation section. Run on `http://localhost:8001`

---

### **Cloud Deployment Guide**

This section provides step-by-step instructions for deploying the Agile Sprint Assistant to various cloud platforms.

---

## ☁️ **CLOUD DEPLOYMENT OPTIONS**

### **Option 1: Google Cloud Run** (Recommended)

**Why Cloud Run?**
- Serverless (no infrastructure management)
- Auto-scaling (0 to N instances)
- Pay only for usage
- Native integration with Google Gemini API
- Simple deployment process

#### **Prerequisites:**

1. **Google Cloud Account**
   - Sign up at [cloud.google.com](https://cloud.google.com)
   - Enable billing (free tier available: $300 credit)

2. **Install Google Cloud SDK**
```bash
   # Download from: https://cloud.google.com/sdk/docs/install
   
   # Verify installation
   gcloud --version
```

3. **Authenticate**
```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
```

#### **Step-by-Step Deployment:**

**Step 1: Prepare Application**

Create `Dockerfile` in project root:
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080

# Run application
CMD cd ui && uvicorn app:app --host 0.0.0.0 --port 8080
```

Create `.dockerignore`:
```
# .dockerignore
venv/
__pycache__/
*.pyc
.env
.git/
*.db
.vscode/
logs/
```

**Step 2: Configure Environment Variables**

Create `env.yaml` (DO NOT commit this file):
```yaml
# env.yaml
GOOGLE_API_KEY: "your-actual-api-key-here"
DATABASE_URL: "sqlite:///database/agile_assistant.db"
SLACK_BOT_TOKEN: "xoxb-your-token-here"
SLACK_CHANNEL_ID: "C0XXXXXXXXX"
SLACK_ENABLED: "true"
```

Add to `.gitignore`:
```
env.yaml
```

**Step 3: Build and Deploy**
```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Set variables
export PROJECT_ID=your-project-id
export SERVICE_NAME=agile-sprint-assistant
export REGION=us-central1

# Build container
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

# Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --env-vars-file env.yaml \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300s \
  --max-instances 10 \
  --min-instances 0
```

**Step 4: Access Application**

After deployment, you'll get a URL like:
```
https://agile-sprint-assistant-xxxxxxxxx-uc.a.run.app
```

**Step 5: Set Up Persistence (Optional)**

By default, SQLite database is ephemeral. For persistence:

**Option A: Use Cloud SQL (PostgreSQL)**
```bash
# Enable Cloud SQL API
gcloud services enable sqladmin.googleapis.com

# Create instance
gcloud sql instances create agile-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=${REGION}

# Create database
gcloud sql databases create agile_assistant \
  --instance=agile-db

# Update env.yaml with Cloud SQL connection string
DATABASE_URL: "postgresql://user:password@/agile_assistant?host=/cloudsql/PROJECT:REGION:agile-db"

# Redeploy with Cloud SQL
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --add-cloudsql-instances PROJECT:REGION:agile-db \
  --env-vars-file env.yaml
```

**Option B: Use Cloud Storage for SQLite**
```bash
# Create bucket
gsutil mb gs://${PROJECT_ID}-agile-db

# Mount bucket in Cloud Run (requires update to app.py)
# Update DATABASE_PATH to use mounted bucket
```

**Step 6: Monitor and Logs**
```bash
# View logs
gcloud run services logs read ${SERVICE_NAME} --region=${REGION}

# View metrics
gcloud run services describe ${SERVICE_NAME} --region=${REGION}
```

**Step 7: Update Application**
```bash
# Make code changes, then:
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --region ${REGION}
```

**Cost Estimate:**
- First 2 million requests/month: FREE
- Cloud Run: ~$0.10 per additional 1M requests
- Cloud SQL: ~$7/month (db-f1-micro)

---

### **Option 2: Heroku**

**Why Heroku?**
- Simple deployment with Git
- Managed database (PostgreSQL)
- Easy environment variable management

#### **Step-by-Step Deployment:**

**Step 1: Install Heroku CLI**
```bash
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login
```

**Step 2: Prepare Application**

Create `Procfile` in project root:
```
web: cd ui && uvicorn app:app --host 0.0.0.0 --port $PORT
```

Create `runtime.txt`:
```
python-3.11.5
```

Update `requirements.txt` to include PostgreSQL:
```
# Add to requirements.txt
psycopg2-binary==2.9.9
```

**Step 3: Create Heroku App**
```bash
# Create app
heroku create agile-sprint-assistant

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini
```

**Step 4: Set Environment Variables**
```bash
heroku config:set GOOGLE_API_KEY=your-api-key
heroku config:set SLACK_BOT_TOKEN=xoxb-your-token
heroku config:set SLACK_CHANNEL_ID=C0XXXXXXXXX
heroku config:set SLACK_ENABLED=true
```

**Step 5: Deploy**
```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Deploy to Heroku
git push heroku main

# Initialize database
heroku run python database/init_db.py

# Open app
heroku open
```

**Step 6: View Logs**
```bash
heroku logs --tail
```

**Cost Estimate:**
- Hobby tier: $7/month (includes PostgreSQL)
- Dyno hours: First 1000 hours/month free

---

### **Option 3: AWS (Elastic Beanstalk)**

**Why AWS EB?**
- Managed platform
- Auto-scaling
- Integrated with AWS ecosystem

#### **Step-by-Step Deployment:**

**Step 1: Install AWS EB CLI**
```bash
pip install awsebcli
```

**Step 2: Initialize EB**
```bash
eb init -p python-3.11 agile-sprint-assistant --region us-east-1
```

**Step 3: Create Environment**
```bash
eb create agile-prod-env
```

**Step 4: Set Environment Variables**
```bash
eb setenv GOOGLE_API_KEY=your-key \
  SLACK_BOT_TOKEN=xoxb-token \
  SLACK_CHANNEL_ID=C0XXXXX \
  SLACK_ENABLED=true
```

**Step 5: Deploy**
```bash
eb deploy
```

**Step 6: Open Application**
```bash
eb open
```

**Cost Estimate:**
- t2.micro (1 GB RAM): ~$8/month
- RDS PostgreSQL: ~$15/month

---

### **Option 4: Docker + Any Cloud VM**

**Why Docker?**
- Platform-agnostic
- Easy to move between providers
- Consistent environment

#### **Deployment to Digital Ocean, Linode, or any VPS:**

**Step 1: Create Droplet/VM**

- OS: Ubuntu 22.04
- RAM: 2GB minimum
- Storage: 25GB

**Step 2: SSH into Server**
```bash
ssh root@your-server-ip
```

**Step 3: Install Docker**
```bash
# Update packages
apt update
apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y
```

**Step 4: Clone Repository**
```bash
git clone https://github.com/PriyankaUtekar/Agile-Sprint-Assistant.git
cd Agile-Sprint-Assistant
```

**Step 5: Create .env File**
```bash
nano .env
```

Add your environment variables (see Configuration section).

**Step 6: Create docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:8080"
    env_file:
      - .env
    volumes:
      - ./database:/app/database
    restart: always
```

**Step 7: Build and Run**
```bash
docker-compose up -d
```

**Step 8: Access Application**
```
http://your-server-ip
```

**Step 9: Set Up SSL (Optional but Recommended)**
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d your-domain.com
```

**Cost Estimate:**
- Digital Ocean Droplet (2GB): $12/month
- Linode Nanode (2GB): $10/month

---

### **Deployment Comparison Table**

| Platform | Ease of Setup | Cost (Monthly) | Auto-Scaling | Database | Best For |
|----------|---------------|----------------|--------------|----------|----------|
| **Google Cloud Run** | ⭐⭐⭐⭐ | ~$5-20 | ✅ Yes | Cloud SQL | Production, auto-scale |
| **Heroku** | ⭐⭐⭐⭐⭐ | $7+ | ✅ Yes | PostgreSQL | Quick deploy, simple |
| **AWS EB** | ⭐⭐⭐ | $20+ | ✅ Yes | RDS | AWS ecosystem |
| **Docker VPS** | ⭐⭐ | $10+ | ❌ No | SQLite/Self-hosted | Full control, custom |

---

### **Post-Deployment Checklist**

- [ ] Application accessible via public URL
- [ ] Environment variables set correctly
- [ ] Database initialized with schema
- [ ] Gemini API working (test with planning agent)
- [ ] Slack notifications working (if enabled)
- [ ] SSL/HTTPS configured (for production)
- [ ] Monitoring/logging set up
- [ ] Backup strategy for database
- [ ] Domain name configured (optional)
- [ ] Authentication added (if needed for production)

---

### **Security Recommendations for Production**

1. **Add Authentication**
```python
   # Add to app.py
   from fastapi import Depends, HTTPException, status
   from fastapi.security import HTTPBasic, HTTPBasicCredentials
   
   security = HTTPBasic()
   
   def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
       # Implement authentication logic
       pass
```

2. **Use HTTPS Only**
   - Configure SSL certificates
   - Redirect HTTP to HTTPS

3. **Rate Limiting**
```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
```

4. **Environment Variable Management**
   - Use secret management services (Google Secret Manager, AWS Secrets Manager)
   - Never commit `.env` or `env.yaml`

5. **Database Backups**
```bash
   # Automated daily backups
   0 2 * * * pg_dump agile_assistant > /backups/backup_$(date +\%Y\%m\%d).sql
```

---

## 🧪 Testing

### **Run Tests**
```bash
# Install testing dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### **Test Coverage**

- Agent functionality tests
- Database operations tests
- API endpoint tests
- Integration tests

---

## 🛠️ Troubleshooting

### **Common Issues**

#### **1. Gemini API Errors**

**Problem:** `API rate limit exceeded`

**Solution:**
```python
# Already implemented in BaseAgent
# Automatic retry with backoff
# Wait 30 seconds and retry
```

**Problem:** `API key not found`

**Solution:**
```bash
# Check .env file
cat .env | grep GOOGLE_API_KEY

# Verify it's loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GOOGLE_API_KEY'))"
```

#### **2. Database Errors**

**Problem:** `Database locked`

**Solution:**
```bash
# SQLite limitation - use PostgreSQL for production
# Or ensure only one process accesses DB
```

**Problem:** `Table doesn't exist`

**Solution:**
```bash
# Re-initialize database
python database/init_db.py
```

#### **3. Slack Integration**

**Problem:** `Slack notifications not working`

**Solution:**
```bash
# Verify credentials
python utils/slack_helper.py

# Check output:
# [Slack] Initialized successfully
```

**Problem:** `Permission denied`

**Solution:**
- Check bot scopes in Slack app settings
- Ensure `chat:write` permission is added
- Reinstall app to workspace

#### **4. Port Already in Use**

**Problem:** `Address already in use: 8001`

**Solution:**
```bash
# Find process using port
# Windows:
netstat -ano | findstr :8001

# Mac/Linux:
lsof -i :8001

# Kill process or use different port
```

---

## 🤝 Contributing

contributions are welcome! Here's how:

### **Development Setup**
```bash
# Fork repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Agile-Sprint-Assistant.git

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes
# ...

# Run tests
pytest

# Commit changes
git commit -m "Add amazing feature"

# Push to your fork
git push origin feature/amazing-feature

# Open Pull Request on GitHub
```


