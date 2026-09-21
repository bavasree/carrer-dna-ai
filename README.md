# OPPORA AI — AI-Powered Student Opportunity Recommendation System

**OPPORA AI** is an end-to-end, production-ready web application designed to bridge the gap between students and high-impact career opportunities. By analyzing student profiles with Google Gemini AI, the platform evaluates Career Readiness Scores, diagnoses skill gaps, recommends curated opportunities (internships, hackathons, certifications, courses, competitions, and jobs), builds personalized 7-stage career roadmaps, enhances resumes with action-verb intelligence, exports styled PDF resumes via ReportLab, and tracks applications via an interactive Kanban board.

---

## 🌟 Key Features

1. **User Authentication & Role Management (Module 1)**
   - Secure student and admin registration with Werkzeug password hashing.
   - JWT-based authentication (`Flask-JWT-Extended`) with automatic session protection and expiration handling.
   - 1-click Demo credentials for rapid testing (`student@oppora.ai` and `admin@oppora.ai`).

2. **Student Profile & Completion Calibration (Module 2)**
   - Full student profile management: personal details, academics, CGPA, graduation year, social links (GitHub, LinkedIn, Portfolio).
   - Skills matrix with proficiency levels (`Beginner`, `Intermediate`, `Advanced`, `Expert`).
   - Project showcase and accredited certification management.
   - Live `profile_completion_pct` weighted calculation.

3. **AI Career Analysis & Competency Diagnostics (Module 3)**
   - Powered by Google Gemini AI with strict-JSON parsing and built-in heuristic fallbacks.
   - Generates a **Career Readiness Score (0–100)**.
   - Evaluates technical strengths, growth opportunities, and missing target competencies.
   - Interactive **Chart.js Competency Benchmark Radar** and **Readiness Gauge**.
   - Role-specific deep-dive skill gap analyzer.

4. **Personalized Opportunity Recommendation Engine (Module 4)**
   - Covers 6 opportunity categories: **Internships, Hackathons, Certifications, Courses, Competitions, and Jobs**.
   - Two-stage hybrid recommendation pipeline: rule-based skill overlap pre-filtering + AI semantic match scoring.
   - Filterable by category, remote status, search queries, and sortable by Match %, Deadline, or Date.
   - Direct bookmarking and 1-click sync to Application Tracker.

5. **7-Stage Career Roadmap Generator (Module 5)**
   - Personalized career roadmap customized to the student's target dream role.
   - 7 sequential stages:
     1. Current Skill Assessment
     2. Skills to Learn
     3. Projects to Build
     4. Certifications to Earn
     5. Internship Preparation
     6. Technical & Behavioral Interview Drills
     7. Placement Preparation & Negotiation
   - Interactive milestone checkboxes, action item completion toggles, and resource links.

6. **AI Resume Builder & ReportLab PDF Generator (Module 6)**
   - Split-screen live interactive document editor and paper preview.
   - AI bullet and career objective enhancer using action verbs and quantified impact metrics.
   - Gemini ATS Compatibility Analyzer with keyword gap diagnosis.
   - Downloadable, professionally styled PDF resumes in **Modern Tech** and **Classic Corporate** templates generated via ReportLab.

7. **Kanban Application Tracker & Pipeline Analytics (Module 7)**
   - Interactive 5-column recruitment pipeline:
     - `Applied` &rarr; `In Progress` &rarr; `Interview Scheduled` &rarr; `Offer Received` &rarr; `Rejected / Archived`
   - HTML5 Drag and Drop card movement between columns.
   - Real-time analytics: Total Applications, Interview Conversion Rate %, Offer Rate %.

8. **Admin Opportunity Management Portal (Module 8)**
   - Role-protected administrative dashboard (`@role_required('admin')`).
   - Full CRUD operations for opportunities with deadline management.
   - Bulk status toggle switches (Activate / Deactivate selected listings).
   - Systemwide distribution analytics.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3 (Custom Glassmorphism Dark Mesh), JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4 |
| **Backend** | Python 3.x, Flask 3.0, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-Limiter, Flask-CORS |
| **Database** | MySQL (SQLAlchemy ORM + PyMySQL driver) |
| **AI Integration** | Google Gemini API (`google-generativeai` SDK) with strict-JSON mode & intelligent heuristic fallbacks |
| **PDF Generation** | ReportLab 5.0 |
| **Template Engine** | Jinja2 |

---

## 📁 Project Structure

```
oppora-ai/
├── backend/
│   ├── app/
│   │   ├── models/                  # Normalized SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # User model & password hashing
│   │   │   ├── profile.py           # StudentProfile, Skill, StudentSkill, StudentProject, StudentCert
│   │   │   ├── opportunity.py       # Opportunity, OpportunityCategory, SavedOpportunity
│   │   │   ├── analysis.py          # CareerAnalysis AI scores & strengths/weaknesses
│   │   │   ├── roadmap.py           # CareerRoadmap & RoadmapMilestones
│   │   │   ├── resume.py            # Resume draft, ATS scores, content snapshots
│   │   │   └── application.py       # Application Kanban model
│   │   ├── routes/                  # Flask Blueprints per module
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py       # /api/auth
│   │   │   ├── profile_routes.py    # /api/profile
│   │   │   ├── analysis_routes.py   # /api/career-analysis
│   │   │   ├── recommendation_routes.py # /api/recommendations
│   │   │   ├── roadmap_routes.py    # /api/roadmap
│   │   │   ├── resume_routes.py     # /api/resume
│   │   │   ├── application_routes.py# /api/applications
│   │   │   ├── admin_routes.py      # /api/admin
│   │   │   └── view_routes.py       # Frontend Jinja template rendering
│   │   ├── services/                # Business logic & AI services
│   │   │   ├── __init__.py
│   │   │   ├── gemini_service.py    # Gemini LLM engine with fallback heuristic
│   │   │   ├── recommendation_engine.py # Hybrid multi-stage matching engine
│   │   │   └── pdf_service.py       # ReportLab PDF resume generator
│   │   └── utils/                   # Decorators, auth, and validators
│   │       ├── __init__.py
│   │       ├── auth_decorators.py   # @jwt_required, @role_required
│   │       └── validators.py        # Input validation helpers
│   ├── config.py                    # Multi-environment configuration
│   ├── run.py                       # Application entry point
│   ├── seed.py                      # Database seeder (skills, categories, opportunities, demo users)
│   ├── schema.sql                   # Raw MySQL schema definitions
│   └── requirements.txt             # Backend Python dependencies
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   ├── variables.css        # Design tokens, themes, glow effects
│   │   │   └── style.css            # Custom glassmorphism, responsive styles
│   │   ├── js/
│   │   │   ├── api.js               # Central API client & toast/loader feedback
│   │   │   ├── auth.js              # Login, register & demo quick-fillers
│   │   │   ├── dashboard.js         # Student dashboard metrics & chart renderers
│   │   │   ├── onboarding.js        # Multi-step onboarding wizard
│   │   │   ├── profile.js           # Student profile & skills/projects CRUD
│   │   │   ├── career_analysis.js   # AI analysis radar & skill-gap modals
│   │   │   ├── recommendations.js   # Filterable opportunity catalog
│   │   │   ├── roadmap.js           # 7-stage interactive timeline & milestones
│   │   │   ├── resume_builder.js    # AI resume editor & PDF preview/download
│   │   │   ├── applications.js      # Drag-and-drop Kanban tracker
│   │   │   └── admin.js             # Admin management & metrics
│   │   └── img/
│   │       ├── logo.svg             # Main vector logo
│   │       └── logo-icon.svg        # Compact icon
│   └── templates/
│       ├── base.html                # Base layout template
│       ├── index.html               # Landing page
│       ├── login.html               # Authentication login
│       ├── register.html            # User registration
│       ├── onboarding.html          # Profile onboarding wizard
│       ├── dashboard.html           # Main student dashboard
│       ├── profile.html             # Profile management
│       ├── career_analysis.html     # AI analysis & radar
│       ├── recommendations.html     # Opportunity explorer
│       ├── roadmap.html             # Interactive career roadmap
│       ├── resume_builder.html      # Resume editor & ATS checker
│       ├── applications.html        # Kanban tracker
│       ├── admin/
│       │   ├── dashboard.html       # Admin stats & control panel
│       │   ├── students.html        # Registered student directory
│       │   ├── opportunities.html   # Opportunity CRUD manager
│       │   └── applications.html    # Global application monitor
│       └── partials/
│           ├── navbar.html          # Navigation header
│           ├── footer.html          # Site footer
│           ├── toast.html           # Bootstrap toast container
│           ├── loading_modal.html   # AI loading spinner modal
│           └── admin_nav.html       # Admin sub-navigation
├── view_database.py                 # Utility script to inspect MySQL database tables
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed
- MySQL Server 8.0+ running locally (or remote MySQL connection)
- A web browser (Chrome, Edge, Firefox)

### 2. Clone or Navigate to Project
```bash
cd "c:\Users\new\OneDrive\Desktop\career DNA AI"
```

### 3. Create & Activate Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 5. Configure Environment Variables (`.env`)
Create or edit `backend/.env` (a pre-configured template is available at `backend/.env.example`):
```ini
# Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=oppora-super-secret-jwt-and-session-key-2025
JWT_SECRET_KEY=oppora-jwt-secret-key-change-in-production-2025
JWT_ACCESS_TOKEN_EXPIRES=86400

# MySQL Database
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=oppora_ai
DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/oppora_ai

# Google Gemini API Key (Optional: leave empty to use built-in intelligent heuristic fallback)
# Get a free key at: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=
```

### 6. Initialize Database & Seed Demo Data
Run the seeder script to create all MySQL tables, seed master skills, categories, 18+ sample opportunities across all 6 types, and create demo user accounts:
```bash
cd backend
python seed.py
```

*Alternatively, you can import `backend/schema.sql` directly into MySQL:*
```bash
mysql -u root -p < schema.sql
```

### 7. Run the Application
Start the Flask development server:
```bash
python run.py
```
Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Pre-Configured Demo Accounts

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Student** | `student@oppora.ai` | `Student@123` | Full student experience (Profile, AI Analysis, Recommendations, Roadmap, Resume, Kanban Tracker) |
| **Admin** | `admin@oppora.ai` | `Admin@123` | Full admin rights (Opportunity CRUD, Analytics, Bulk Status) |

*You can also click the **⚡ Student Demo** or **⚡ Admin Demo** buttons directly on the Login page for 1-click authentication.*

---

## 🧪 Verification & Testing

An end-to-end automated test script verifies all 8 API modules:
```bash
cd backend
python -c "
import urllib.request, json
res = urllib.request.urlopen('http://127.0.0.1:5000/api/recommendations')
data = json.loads(res.read())
print('API Recommendations Status:', data.get('success'), '| Count:', len(data.get('data', {}).get('opportunities', [])))
"
```

---

## 📄 License
MIT License. Built for student career acceleration.
