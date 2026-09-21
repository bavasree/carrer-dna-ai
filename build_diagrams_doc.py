import os
import sys
import base64
import json
import urllib.request
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

DIAGRAMS_DIR = os.path.join(os.path.dirname(__file__), "diagram_images")
os.makedirs(DIAGRAMS_DIR, exist_ok=True)

DIAGRAMS_DATA = [
    {
        "id": "1_system_architecture",
        "title": "1. System Architecture Diagram",
        "figure_no": "Figure 1.1",
        "caption": "Multi-Tier Decoupled System Architecture of OPPORA AI",
        "desc": "The System Architecture comprises a 5-tier topology: (1) Client Presentation Layer with responsive glassmorphism dark mesh CSS, Bootstrap 5.3, and Chart.js 4.4; (2) Security & Gateway Layer enforcing Flask-JWT-Extended authentication, Flask-Limiter rate limits, and CORS policies; (3) Application & Controller Layer structuring 8 Flask Blueprints; (4) Intelligence & Service Layer housing GeminiService, RecommendationEngine, and PDFService; (5) Persistence Layer backed by MySQL 8.0 with PyMySQL connection pooling and foreign key cascades.",
        "mermaid": """flowchart TB
    subgraph ACTORS ["👥 User Roles & Clients"]
        direction LR
        STUDENT["🎓 Student / Job Seeker\n(Desktop / Mobile Browser)"]
        ADMIN["🛡️ System Administrator\n(Admin Management Portal)"]
    end

    subgraph PRESENTATION ["🌐 Presentation & Frontend Layer (HTML5 / CSS / ES6 JS)"]
        direction TB
        UI_AUTH["🔐 Auth Pages (login, register)"]
        UI_DASH["📊 Student Dashboard (radar charts)"]
        UI_PROFILE["👤 Profile & Skills Matrix"]
        UI_ANALYSIS["🧠 AI Career Analysis & Gap Audit"]
        UI_OPP["🎯 Opportunity Catalog (filters/search)"]
        UI_ROADMAP["🗺️ 7-Stage Career Roadmap"]
        UI_RESUME["📄 AI Resume Builder & Preview"]
        UI_KANBAN["📋 Application Kanban Tracker"]
        UI_ADMIN["⚙️ Admin Control Center"]
    end

    subgraph GATEWAY ["🔒 Security, Routing & Middleware Layer"]
        direction TB
        REVERSE_PROXY["🌐 Web Server / WSGI Gateway"]
        JWT_GUARD["🔑 JWT Security Guard (Token Validation & Claims)"]
        RATE_LIMIT["⏱️ Flask-Limiter (Rate Limiter)"]
        CORS_SEC["🛡️ Flask-CORS Security Headers"]
    end

    subgraph BACKEND ["⚙️ Flask Backend Core Application Layer (Python 3.x / Flask 3.0)"]
        direction TB
        subgraph BLUEPRINTS ["📌 Flask Blueprints & REST Endpoints"]
            BP_AUTH["/api/auth (login, register, me)"]
            BP_PROF["/api/profile (CRUD profile, skills, projects)"]
            BP_ANALYSIS["/api/career-analysis (run audit, gaps)"]
            BP_REC["/api/recommendations (matching, filters)"]
            BP_ROAD["/api/roadmap (7 stages, milestone toggle)"]
            BP_RES["/api/resume (drafts, ATS score, PDF)"]
            BP_APP["/api/applications (Kanban CRUD, stats)"]
            BP_ADMIN["/api/admin (stats, manage opps, bulk toggle)"]
        end

        subgraph ORM_LAYER ["🗄️ ORM Data Access Layer (Flask-SQLAlchemy)"]
            MODELS["📦 14 Normalized Domain Models\nUser • StudentProfile • Skill • StudentSkill • StudentProject\nStudentCertification • OpportunityCategory • Opportunity\nSavedOpportunity • CareerAnalysis • CareerRoadmap\nRoadmapMilestone • Resume • Application"]
        end
    end

    subgraph SERVICES ["🧠 Business Logic & Service Engines"]
        direction TB
        REC_ENGINE["🔍 RecommendationEngine\n• Rule-based Multi-Facet Filter\n• 4-Factor DNA Match Scorer\n• Deadline Urgency Prioritizer"]
        GEMINI_SVC["🤖 GeminiService\n• Multi-Model Waterfall Fallback\n• 10s Strict Request Timeout\n• Defensive Strict-JSON Parser\n• Algorithmic Fallback Engine"]
        PDF_SVC["📑 PDFService\n• ReportLab 5.0 Flowable Engine\n• Modern & Classic Templates\n• ATS-Compliant Layout Generator"]
    end

    subgraph AI_CLOUD ["☁️ Google Gemini Generative AI Platform"]
        direction TB
        GEMINI_API["🚀 Google Gemini API Endpoints\n(gemini-2.5-flash / gemini-2.0-flash / gemini-1.5-flash)"]
    end

    subgraph DATABASE ["💾 Persistence Layer (MySQL Relational Database)"]
        direction TB
        MYSQL_DB[("🛢️ MySQL 8.x Database Engine\n• PyMySQL Connection Pool\n• FK Cascade Constraints\n• Multi-Column Indexes")]
    end

    STUDENT -->|HTTP/HTTPS REST & HTML| REVERSE_PROXY
    ADMIN -->|HTTP/HTTPS REST & Admin Views| REVERSE_PROXY
    REVERSE_PROXY --> RATE_LIMIT --> CORS_SEC --> JWT_GUARD --> BLUEPRINTS
    BLUEPRINTS --> PRESENTATION
    BLUEPRINTS --> SERVICES
    SERVICES --> ORM_LAYER --> MYSQL_DB
    GEMINI_SVC -->|HTTPS API with JSON Schema| GEMINI_API
    REC_ENGINE --> GEMINI_SVC
    PDF_SVC -->|Binary Bytes Stream| BP_RES
    BP_RES -->|Download Stream| STUDENT"""
    },
    {
        "id": "2a_dfd_level_0",
        "title": "2.1 Data Flow Diagram (DFD) — Level 0 Context Diagram",
        "figure_no": "Figure 2.1",
        "caption": "Level 0 Context Data Flow Diagram for OPPORA AI System",
        "desc": "The Context Diagram models the overarching system boundary. The Student user exchanges authentication credentials, profile competencies, opportunity query filters, and resume drafts for JWT tokens, readiness scores, recommendations, and PDF resumes. The Administrator oversees opportunity listings and inspects analytics. The central engine coordinates with Google Gemini AI via strict JSON payloads.",
        "mermaid": """flowchart TD
    STUDENT(["🎓 Student User"])
    ADMIN(["🛡️ Administrator"])
    GEMINI(["🤖 Google Gemini AI API"])

    SYSTEM[["0.0\nOPPORA AI\nCentral System"]]

    STUDENT -->|"1. Credentials & Registration\n2. Profile Data (Skills, Projects, CGPA, Goal)\n3. Search Queries & Filter Parameters\n4. Roadmap Action Item Toggles\n5. Resume Drafts & Target Roles\n6. Application Status Updates"| SYSTEM

    SYSTEM -->|"1. Signed JWT Tokens\n2. Career Readiness Score & Radar JSON\n3. Ranked Recommendations & Match Diagnostics\n4. 7-Stage Milestone Action Plan\n5. ATS Score & Keyword Improvement Feedback\n6. ReportLab Binary PDF Resumes\n7. Kanban Pipeline Metrics"| STUDENT

    ADMIN -->|"1. Admin Credentials\n2. Opportunity Creation / Edit / Delete Payloads\n3. Status Toggles (Active / Inactive)\n4. Student Audit Actions"| SYSTEM

    SYSTEM -->|"1. System-wide Analytics & Counters\n2. Registered Students & Profiles\n3. Opportunity Audit Logs"| ADMIN

    SYSTEM -->|"1. Structured Profile JSON\n2. Target Role Benchmarks & Skill Sets\n3. Resume Text Corpus & Job Description"| GEMINI

    GEMINI -->|"1. Career Diagnosis JSON (Strengths/Gaps)\n2. 7-Stage Milestone Plan JSON\n3. Action-Verb Bullet Rewrites & ATS Keyword Audit"| SYSTEM"""
    },
    {
        "id": "2b_dfd_level_1",
        "title": "2.2 Data Flow Diagram (DFD) — Level 1 Subsystem Flow",
        "figure_no": "Figure 2.2",
        "caption": "Level 1 Subsystem Data Flow Diagram across 8 Functional Processes and 7 Data Stores",
        "desc": "Level 1 DFD decomposes the system into 8 distinct processes: 1.0 Auth & Session Management, 2.0 Profile & Competency Management, 3.0 AI Career Readiness Diagnostic Engine, 4.0 Hybrid Opportunity Recommendation Engine, 5.0 7-Stage Career Roadmap Generator, 6.0 AI Resume Builder & PDF Service, 7.0 Kanban Application Tracker, and 8.0 Admin Management. Data stores D1 to D7 reflect the underlying MySQL relational tables.",
        "mermaid": """flowchart TB
    STUDENT(["🎓 Student"])
    ADMIN(["🛡️ Administrator"])
    GEMINI(["🤖 Google Gemini AI"])

    subgraph DATA_STORES ["🗄️ Relational Data Stores"]
        D1[("D1: Users")]
        D2[("D2: Student Profiles & Skills")]
        D3[("D3: Opportunities & Categories")]
        D4[("D4: Career Analyses")]
        D5[("D5: Roadmaps & Milestones")]
        D6[("D6: Resumes & ATS Cache")]
        D7[("D7: Applications")]
    end

    P1[["1.0\nAuthentication &\nSession Management"]]
    P2[["2.0\nProfile & Competency\nManagement"]]
    P3[["3.0\nAI Career Readiness\n& Gap Analysis"]]
    P4[["4.0\nHybrid Opportunity\nRecommendation Engine"]]
    P5[["5.0\n7-Stage Career\nRoadmap Generator"]]
    P6[["6.0\nAI Resume Builder\n& PDF Service"]]
    P7[["7.0\nKanban Application\nTracker & Analytics"]]
    P8[["8.0\nAdmin Management\n& Opportunity CRUD"]]

    STUDENT -->|"Credentials"| P1
    ADMIN -->|"Admin Credentials"| P1
    P1 -->|"Verify / Hash"| D1
    D1 -->|"User Role"| P1
    P1 -->|"JWT Token"| STUDENT
    P1 -->|"Admin Token"| ADMIN

    STUDENT -->|"Profile fields, Skills, Projects"| P2
    P2 -->|"Write / Calc Completion %"| D2
    D2 -->|"Profile Snapshot"| P2
    P2 -->|"Updated Profile Data"| STUDENT

    STUDENT -->|"Request Career Audit"| P3
    D2 -->|"Fetch Profile"| P3
    P3 -->|"Context Prompt"| GEMINI
    GEMINI -->|"Readiness JSON"| P3
    P3 -->|"Save Analysis"| D4
    P3 -->|"Render Radar & Score"| STUDENT

    STUDENT -->|"Filters, Mode, Category"| P4
    D3 -->|"Active Listings"| P4
    D2 -->|"Student DNA Vector"| P4
    P4 -->|"4-Factor Fit Score"| P4
    P4 -->|"Ranked Matches"| STUDENT
    P4 -->|"Save Bookmark"| D3

    STUDENT -->|"Target Role & Toggle Items"| P5
    D2 -->|"Academics & Skills"| P5
    P5 -->|"Prompt: 7 Stages"| GEMINI
    GEMINI -->|"Milestones JSON"| P5
    P5 -->|"Store Roadmap"| D5
    D5 -->|"Fetch Milestones"| P5
    P5 -->|"Interactive Checklist"| STUDENT

    STUDENT -->|"Resume Text & Refine"| P6
    D2 -->|"Autofill Profile"| P6
    P6 -->|"ATS Prompt"| GEMINI
    GEMINI -->|"Enhanced Bullets"| P6
    P6 -->|"Persist Resume"| D6
    P6 -->|"Download Stream (.pdf)"| STUDENT

    STUDENT -->|"Apply / Drag Card"| P7
    P7 -->|"Update Kanban Status"| D7
    D7 -->|"Fetch Cards by Stage"| P7
    P7 -->|"Pipeline Metrics"| STUDENT

    ADMIN -->|"Add/Edit/Delete Listing"| P8
    P8 -->|"Update Catalog"| D3
    D1 -->|"User Counts"| P8
    D7 -->|"Pipeline Totals"| P8
    P8 -->|"Analytics Table"| ADMIN"""
    },
    {
        "id": "2c_dfd_level_2_rec",
        "title": "2.3 Data Flow Diagram (DFD) — Level 2.1 AI Career Analysis & Recommendation Subsystem",
        "figure_no": "Figure 2.3",
        "caption": "Level 2 Decomposed DFD for Processes 3.0 (AI Career Analysis) and 4.0 (Hybrid Recommendations)",
        "desc": "Decomposes the recommendation and career readiness subsystem into precise operational steps: Profile DNA aggregation (3.1), Gemini waterfall invocation (3.2), readiness score computation (3.3), analysis persistence (3.4), SQL pre-filtering (4.1), keyword search (4.2), 4-factor scoring (4.3), and post-filter pruning with explainability rationale generation (4.4).",
        "mermaid": """flowchart TB
    STUDENT(["🎓 Student"])
    GEMINI(["🤖 Google Gemini AI"])
    D2[("D2: Student Profiles & Skills")]
    D3[("D3: Opportunities Catalog")]
    D4[("D4: Career Analyses")]

    P3_1[["3.1 Aggregate Profile DNA\n(Skills, CGPA, Projects, Goal)"]]
    P3_2[["3.2 Dispatch Prompt & Fallback Handler\n(Multi-Model Waterfall + 10s Timeout)"]]
    P3_3[["3.3 Calculate Readiness Score (0-100)\n& Identify Missing Competencies"]]
    P3_4[["3.4 Persist Career Analysis Record\n& Generate Radar Chart JSON"]]

    P4_1[["4.1 Pre-Filter Base Query\n(Active, Non-expired, Type, Mode, Fee)"]]
    P4_2[["4.2 Multi-Field Keyword & Fuzzy Search\n(Title, Description, Required Skills)"]]
    P4_3[["4.3 4-Factor Weighted Match Scoring\n• Skills Overlap (45%)\n• Career Alignment (30%)\n• Eligibility Fit (15%)\n• Projects/Exp (10%)"]]
    P4_4[["4.4 Post-Scoring Prune & Ranking\n(Min Match, Urgent <7 Days, Sort Desc)"]]

    STUDENT -->|"Trigger Analysis"| P3_1
    D2 -->|"Read Profile"| P3_1
    P3_1 -->|"Sanitized JSON Profile"| P3_2
    P3_2 -->|"LLM Prompt"| GEMINI
    GEMINI -->|"Raw AI Output"| P3_2
    P3_2 -->|"Parsed JSON / Fallback"| P3_3
    P3_3 -->|"Scores & Lists"| P3_4
    P3_4 -->|"Save Record"| D4
    P3_4 -->|"Rendered Audit & Radar"| STUDENT

    STUDENT -->|"Apply Search / Filters"| P4_1
    D3 -->|"Read Catalog"| P4_1
    P4_1 -->|"Filtered Query"| P4_2
    P4_2 -->|"Candidate Opportunity List"| P4_3
    D2 -->|"Student Skills Vector"| P4_3
    P4_3 -->|"Scored Opportunity Stream"| P4_4
    P4_4 -->|"Ranked Recommendations & Diagnostics"| STUDENT"""
    },
    {
        "id": "2d_dfd_level_2_resume",
        "title": "2.4 Data Flow Diagram (DFD) — Level 2.2 AI Resume Builder & Kanban Application Tracker",
        "figure_no": "Figure 2.4",
        "caption": "Level 2 Decomposed DFD for Processes 6.0 (Resume Builder) and 7.0 (Kanban Application Pipeline)",
        "desc": "Decomposes the AI resume compilation and application tracking subsystems into operational subprocesses: profile autofill (6.1), AI action-verb bullet refinement (6.2), ATS keyword density audit (6.3), draft storage (6.4), ReportLab PDF rendering (6.5), application ingestion (7.1), state machine card drag-and-drop transitions (7.2), and pipeline analytics calculation (7.3).",
        "mermaid": """flowchart TB
    STUDENT(["🎓 Student"])
    GEMINI(["🤖 Google Gemini AI"])
    D2[("D2: Student Profile")]
    D6[("D6: Resumes")]
    D7[("D7: Applications")]

    P6_1[["6.1 Ingest & Sync Profile Data\n(Autopopulate Contact, Education, Skills, Projects)"]]
    P6_2[["6.2 AI Section & Bullet Refinement\n(Inject Action Verbs, Metrics & Impact)"]]
    P6_3[["6.3 ATS Friendliness & Keyword Audit\n(Target Role Comparison & Gap Detection)"]]
    P6_4[["6.4 Save Resume Draft\n(Store JSON Snapshot & ATS Score in DB)"]]
    P6_5[["6.5 ReportLab PDF Rendering Engine\n(Apply Typography, Tables, Dividers & Margins)"]]

    P7_1[["7.1 Ingest Opportunity Application\n(Store Company, Role, Type, Initial 'Applied' Status)"]]
    P7_2[["7.2 Handle Kanban State Transition\n(Move to InProgress, Interview, Offer, Rejected)"]]
    P7_3[["7.3 Compute Pipeline Analytics\n(Total Count, Interview Rate %, Offer Success %)"]]

    STUDENT -->|"Open Resume Builder"| P6_1
    D2 -->|"Extract Profile Data"| P6_1
    P6_1 -->|"Initial Resume State"| STUDENT

    STUDENT -->|"Click 'AI Enhance Bullet'"| P6_2
    P6_2 -->|"Enhance Prompt"| GEMINI
    GEMINI -->|"Action-Oriented Text JSON"| P6_2
    P6_2 -->|"Refined Text Preview"| STUDENT

    STUDENT -->|"Request ATS Score"| P6_3
    P6_3 -->|"Scan Keywords vs Target Role"| GEMINI
    GEMINI -->|"ATS Score (0-100) & Missing Keywords"| P6_3
    P6_3 -->|"ATS Gauge & Fix List"| STUDENT

    STUDENT -->|"Save Resume"| P6_4
    P6_4 -->|"Write State"| D6

    STUDENT -->|"Click 'Download PDF'"| P6_5
    D6 -->|"Read Snapshot"| P6_5
    D2 -->|"Read Full Academics"| P6_5
    P6_5 -->|"Stream PDF Bytes"| STUDENT

    STUDENT -->|"Click 'Apply' / Add Card"| P7_1
    P7_1 -->|"Persist Application"| D7
    STUDENT -->|"Drag Card to New Stage Column"| P7_2
    P7_2 -->|"Update Status"| D7
    D7 -->|"Fetch Cards by Column"| P7_3
    P7_3 -->|"Render Kanban Columns & Metrics"| STUDENT"""
    },
    {
        "id": "3a_uml_use_case",
        "title": "3.1 UML Use Case Diagram",
        "figure_no": "Figure 3.1",
        "caption": "UML Use Case Diagram Depicting Student, Administrator, and Gemini AI Engine Interactions",
        "desc": "Models 21 discrete use cases encapsulated within the OPPORA AI system boundary. Students execute profile management, AI career readiness audits, opportunity recommendations, 7-stage roadmap tracking, AI resume builder with ATS scoring, ReportLab PDF export, and Kanban application tracking. Administrators perform opportunity CRUD, toggle statuses, and view distribution metrics. Gemini AI acts as a secondary actor executing generative NLP tasks.",
        "mermaid": """flowchart LR
    STUDENT((🎓 Student User))
    ADMIN((🛡️ Administrator))
    GEMINI((🤖 Gemini AI Engine))

    subgraph SYSTEM ["📦 OPPORA AI System"]
        direction TB
        UC1(["UC-01: Register & Authenticate (JWT)"])
        UC2(["UC-02: Manage Student Profile & Skills"])
        UC3(["UC-03: View Profile Completion % Gauge"])
        UC4(["UC-04: Execute AI Career Readiness Assessment"])
        UC5(["UC-05: View Competency Radar & Skill Gaps"])
        UC6(["UC-06: Explore & Filter Career Opportunities"])
        UC7(["UC-07: Inspect Match % & DNA Breakdown"])
        UC8(["UC-08: Bookmark / Save Opportunities"])
        UC9(["UC-09: Generate 7-Stage Career Roadmap"])
        UC10(["UC-10: Toggle Roadmap Action Items & Milestones"])
        UC11(["UC-11: Build AI Resume with Live Preview"])
        UC12(["UC-12: AI Enhance Bullets with Action Verbs"])
        UC13(["UC-13: Run ATS Friendliness Diagnostic"])
        UC14(["UC-14: Export PDF Resume (ReportLab)"])
        UC15(["UC-15: Manage Applications in Kanban Pipeline"])
        UC16(["UC-16: Drag & Drop Kanban Stage Transition"])
        UC17(["UC-17: Access Admin Portal (Role-Protected)"])
        UC18(["UC-18: Create / Edit / Delete Opportunity"])
        UC19(["UC-19: Toggle Opportunity Status (Active/Inactive)"])
        UC20(["UC-20: View System-Wide Metrics & Distribution"])
        UC21(["UC-21: Audit Student Profiles & Applications"])
    end

    STUDENT --> UC1
    STUDENT --> UC2
    STUDENT --> UC3
    STUDENT --> UC4
    STUDENT --> UC6
    STUDENT --> UC8
    STUDENT --> UC9
    STUDENT --> UC10
    STUDENT --> UC11
    STUDENT --> UC14
    STUDENT --> UC15
    STUDENT --> UC16

    UC4 -.->|«include»| UC5
    UC6 -.->|«include»| UC7
    UC11 -.->|«extend»| UC12
    UC11 -.->|«extend»| UC13

    ADMIN --> UC1
    ADMIN --> UC17
    ADMIN --> UC18
    ADMIN --> UC19
    ADMIN --> UC20
    ADMIN --> UC21

    UC4 -.->|«delegates LLM»| GEMINI
    UC9 -.->|«delegates LLM»| GEMINI
    UC12 -.->|«delegates LLM»| GEMINI
    UC13 -.->|«delegates LLM»| GEMINI"""
    },
    {
        "id": "3b_uml_class",
        "title": "3.2 UML Class Diagram",
        "figure_no": "Figure 3.2",
        "caption": "UML Class Diagram Depicting Domain Models, Service Classes, Attributes, Methods, and Associations",
        "desc": "Presents the structural design of the platform. Encapsulates 14 SQLAlchemy entity models (User, StudentProfile, Skill, StudentSkill, StudentProject, StudentCertification, OpportunityCategory, Opportunity, SavedOpportunity, CareerAnalysis, CareerRoadmap, RoadmapMilestone, Resume, Application) alongside the 3 singleton services (GeminiService, RecommendationEngine, PDFService). Multiplicities, associations, and composition relationships are strictly preserved.",
        "mermaid": """classDiagram
    direction TB
    class User {
        +int id
        +string email
        +string password_hash
        +string role
        +bool is_active
        +datetime created_at
        +set_password(password) void
        +check_password(password) bool
        +to_dict() dict
    }

    class StudentProfile {
        +int id
        +int user_id
        +string full_name
        +string headline
        +string degree
        +string branch
        +float cgpa
        +string career_goal
        +string target_role
        +int profile_completion_pct
        +calculate_completion_pct() int
        +to_dict() dict
    }

    class Skill {
        +int id
        +string name
        +string category
        +to_dict() dict
    }

    class StudentSkill {
        +int id
        +int student_id
        +int skill_id
        +string skill_name
        +string proficiency_level
        +float years_of_experience
        +to_dict() dict
    }

    class Opportunity {
        +int id
        +int category_id
        +string title
        +string company_name
        +string opportunity_type
        +text description
        +string event_mode
        +string registration_fee
        +datetime deadline
        +string required_skills_json
        +string status
        +required_skills() list
        +to_dict(student_id) dict
    }

    class CareerAnalysis {
        +int id
        +int student_id
        +int readiness_score
        +text strengths_json
        +text skill_gaps_json
        +text recommended_roles_json
        +text ai_summary
        +strengths() list
        +skill_gaps() list
        +to_dict() dict
    }

    class CareerRoadmap {
        +int id
        +int student_id
        +string target_role
        +int overall_progress
        +calculate_progress() int
        +to_dict() dict
    }

    class RoadmapMilestone {
        +int id
        +int roadmap_id
        +int stage_number
        +string stage_name
        +string title
        +text action_items_json
        +text resources_json
        +bool is_completed
        +to_dict() dict
    }

    class Resume {
        +int id
        +int student_id
        +string title
        +string template_name
        +int ats_score
        +text content_data_json
        +content_data() dict
        +to_dict() dict
    }

    class Application {
        +int id
        +int student_id
        +int opportunity_id
        +string company_name
        +string position_title
        +string status
        +date applied_date
        +to_dict() dict
    }

    class GeminiService {
        -string api_key
        -string active_model_name
        +analyze_career(profile_data) dict
        +analyze_skill_gap(profile_data, role) dict
        +calculate_match_score(profile, opp) dict
        +generate_roadmap(profile, role) list
        +improve_resume_section(type, text) dict
        +score_resume_ats(resume_data, role) dict
    }

    class RecommendationEngine {
        +get_recommendations(profile, filters, limit) list
        +get_opportunity_detail(opp_id, profile) dict
    }

    class PDFService {
        +generate_resume_pdf(resume, profile, template) BytesIO
    }

    User "1" *-- "1" StudentProfile : has profile
    StudentProfile "1" *-- "0..*" StudentSkill : has
    Skill "0..1" <-- "0..*" StudentSkill : references
    StudentProfile "1" *-- "0..*" CareerAnalysis : records
    StudentProfile "1" *-- "0..*" CareerRoadmap : follows
    CareerRoadmap "1" *-- "1..7" RoadmapMilestone : contains
    StudentProfile "1" *-- "0..*" Resume : drafts
    StudentProfile "1" *-- "0..*" Application : submits
    Opportunity "0..1" <-- "0..*" Application : links
    RecommendationEngine ..> Opportunity : queries
    RecommendationEngine ..> GeminiService : invokes match scoring
    GeminiService ..> CareerAnalysis : computes
    PDFService ..> Resume : renders"""
    },
    {
        "id": "3c_uml_seq_auth_analysis",
        "title": "3.3 UML Sequence Diagram 1 — Authentication, Profile Synchronization & AI Career Readiness Audit",
        "figure_no": "Figure 3.3",
        "caption": "UML Sequence Diagram: User Authentication, Profile Sync & AI Career Readiness Assessment",
        "desc": "Illustrates the chronological message flow between the Student Client, Auth Blueprint, Career Analysis Controller, GeminiService singleton, Google Gemini Cloud LLM, and MySQL Database. Enforces 10s timeouts and fallback handling.",
        "mermaid": """sequenceDiagram
    autonumber
    actor Student as 🎓 Student User
    participant Browser as 🌐 Client Browser (JS/Fetch)
    participant AuthRoute as 🔑 /api/auth
    participant AnalysisRoute as 🧠 /api/career-analysis
    participant GeminiSvc as 🤖 GeminiService
    participant GeminiAPI as ☁️ Google Gemini API
    participant DB as 💾 MySQL Database

    Student->>Browser: Enters email & password
    Browser->>AuthRoute: POST /api/auth/login {email, password}
    AuthRoute->>DB: Query User by email
    DB-->>AuthRoute: User record (password_hash, role)
    AuthRoute->>AuthRoute: check_password_hash()
    AuthRoute-->>Browser: HTTP 200 {access_token, user: {...}}
    Browser->>Browser: Store JWT in localStorage

    Student->>Browser: Clicks "Run AI Career Audit"
    Browser->>AnalysisRoute: POST /api/career-analysis/run (Headers: Bearer JWT)
    AnalysisRoute->>DB: Query StudentProfile (Skills, Projects, CGPA, Goal)
    DB-->>AnalysisRoute: StudentProfile domain object
    AnalysisRoute->>GeminiSvc: analyze_career(profile_data)

    GeminiSvc->>GeminiAPI: GenerateContent(Prompt, timeout=10s)
    alt Gemini API Returns Valid JSON within 10s
        GeminiAPI-->>GeminiSvc: JSON: {readiness_score: 84, strengths: [...], skill_gaps: [...]}
    else Timeout or API Key Missing / Rate-Limited
        GeminiSvc->>GeminiSvc: Execute _fallback_career_analysis() algorithm
    end

    GeminiSvc-->>AnalysisRoute: Structured Analysis Dict
    AnalysisRoute->>DB: INSERT into career_analyses (...)
    DB-->>AnalysisRoute: Commit OK (analysis_id=42)
    AnalysisRoute-->>Browser: HTTP 200 JSON {success: true, analysis: {...}}
    Browser->>Browser: Render Chart.js Competency Radar & Gauge (84/100)
    Browser-->>Student: Displays Technical Strengths, Growth Areas & Target Roles"""
    },
    {
        "id": "3d_uml_seq_rec_kanban",
        "title": "3.4 UML Sequence Diagram 2 — Hybrid Opportunity Matching & Kanban Pipeline State Transition",
        "figure_no": "Figure 3.4",
        "caption": "UML Sequence Diagram: Hybrid Opportunity Matching and Drag-and-Drop Kanban State Transition",
        "desc": "Models the interactions between the Student Client, Recommendation Controller, RecommendationEngine, GeminiService, Application Blueprint, and MySQL Database. Covers 4-factor scoring and Kanban card movement with stage transition updates.",
        "mermaid": """sequenceDiagram
    autonumber
    actor Student as 🎓 Student User
    participant Browser as 🌐 Client Browser
    participant RecRoute as 🎯 /api/recommendations
    participant RecEngine as 🔍 RecommendationEngine
    participant GeminiSvc as 🤖 GeminiService
    participant AppRoute as 📋 /api/applications
    participant DB as 💾 MySQL Database

    Student->>Browser: Selects filters (Category="Internship", Mode="Remote", MinMatch=70)
    Browser->>RecRoute: GET /api/recommendations?type=internship&is_remote=true&min_match=70
    RecRoute->>DB: Query StudentProfile (Skills, Target Role, Degree)
    DB-->>RecRoute: Profile Data
    RecRoute->>RecEngine: get_recommendations(profile, filters)
    RecEngine->>DB: Query Opportunities (status='active', deadline >= now)
    DB-->>RecEngine: List of Active Opportunity Records

    loop For each candidate opportunity
        RecEngine->>GeminiSvc: calculate_match_score(profile_data, opp_dict)
        GeminiSvc->>GeminiSvc: 4-Factor Weighted Calculation (45/30/15/10)
        GeminiSvc-->>RecEngine: {match_score: 88, matched_skills: [...], missing_skills: [...]}
    end

    RecEngine->>RecEngine: Filter by min_match >= 70 & Sort by match_score DESC
    RecEngine-->>RecRoute: List of Scored Opportunities
    RecRoute-->>Browser: HTTP 200 JSON [{id: 12, title: "SDE Intern", match_score: 88, ...}]
    Browser-->>Student: Displays opportunity cards with Match % & DNA diagnostics

    Student->>Browser: Clicks "Apply / Add to Kanban"
    Browser->>AppRoute: POST /api/applications {opportunity_id: 12, company_name: "Google", status: "applied"}
    AppRoute->>DB: INSERT into applications (student_id, opportunity_id, status='applied', ...)
    DB-->>AppRoute: Commit OK (application_id=105)
    AppRoute-->>Browser: HTTP 201 {success: true, application: {...}}

    Student->>Browser: Drags card from "Applied" to "Interview Scheduled"
    Browser->>AppRoute: PUT /api/applications/105/status {status: "interview", interview_date: "2026-10-15"}
    AppRoute->>DB: UPDATE applications SET status='interview' WHERE id=105
    DB-->>AppRoute: Commit OK
    AppRoute-->>Browser: HTTP 200 {success: true, updated_metrics: {...}}
    Browser-->>Student: Kanban Board & Interview Conversion Rate % updated live"""
    },
    {
        "id": "3e_uml_seq_resume_pdf",
        "title": "3.5 UML Sequence Diagram 3 — AI Resume Enhancement, ATS Scoring & ReportLab PDF Generation",
        "figure_no": "Figure 3.5",
        "caption": "UML Sequence Diagram: AI Resume Bullet Optimization, ATS Scoring & ReportLab PDF Generation",
        "desc": "Details the interactive split-screen resume builder workflow. Covers AI action-verb bullet refinement, ATS keyword density diagnostics, draft persistence in MySQL, and server-side ReportLab compilation into in-memory BytesIO streams delivered as downloadable attachments.",
        "mermaid": """sequenceDiagram
    autonumber
    actor Student as 🎓 Student User
    participant Browser as 🌐 Client Browser
    participant ResumeRoute as 📄 /api/resume
    participant GeminiSvc as 🤖 GeminiService
    participant PDFSvc as 📑 PDFService
    participant DB as 💾 MySQL Database

    Student->>Browser: Enters raw bullet: "Made a website using Flask and MySQL"
    Student->>Browser: Clicks "AI Enhance"
    Browser->>ResumeRoute: POST /api/resume/improve-section {section: "project", text: "..."}
    ResumeRoute->>GeminiSvc: improve_resume_section("project", text, context)
    GeminiSvc->>GeminiSvc: Inject action verbs, performance metrics & ATS keywords
    GeminiSvc-->>ResumeRoute: {improved_text: "• Architected high-throughput web app with Flask...", keywords: [...]}
    ResumeRoute-->>Browser: HTTP 200 JSON {improved_text: "..."}
    Browser-->>Student: Updates textarea with quantified action-oriented bullet

    Student->>Browser: Clicks "Run ATS Scanner" (Target: "Full-Stack Engineer")
    Browser->>ResumeRoute: POST /api/resume/score-ats {resume_data: {...}, target_role: "Full-Stack Engineer"}
    ResumeRoute->>GeminiSvc: score_resume_ats(resume_data, "Full-Stack Engineer")
    GeminiSvc-->>ResumeRoute: {ats_score: 91, keyword_density: 88, missing_keywords: ["Docker", "CI/CD"]}
    ResumeRoute->>DB: UPDATE resumes SET ats_score=91, ats_feedback_json=...
    DB-->>ResumeRoute: Commit OK
    ResumeRoute-->>Browser: HTTP 200 JSON {ats_score: 91, feedback: {...}}
    Browser-->>Student: Renders circular ATS Score dial & missing keyword badges

    Student->>Browser: Clicks "Export PDF (Modern Template)"
    Browser->>ResumeRoute: GET /api/resume/download-pdf?template=modern
    ResumeRoute->>DB: Query Resume & StudentProfile models
    DB-->>ResumeRoute: Full Models & Child Collections
    ResumeRoute->>PDFSvc: generate_resume_pdf(resume_obj, profile_obj, template='modern')
    PDFSvc->>PDFSvc: Compile ReportLab SimpleDocTemplate (Navy accents, two-column tables)
    PDFSvc-->>ResumeRoute: BytesIO in-memory buffer
    ResumeRoute-->>Browser: HTTP 200 Response (application/pdf attachment)
    Browser-->>Student: Downloads formatted, ATS-compliant PDF resume file"""
    },
    {
        "id": "4_er_diagram",
        "title": "4. Entity-Relationship (ER) Diagram",
        "figure_no": "Figure 4.1",
        "caption": "Complete Normalized Entity-Relationship (ER) Diagram with Referential Integrity Constraints",
        "desc": "Presents the Third Normal Form (3NF) relational database schema spanning 14 tables in MySQL. Demonstrates 1:1 association between Users and StudentProfiles; 1:N relations for Skills, Projects, Certifications, Roadmaps, Milestones, Resumes, and Applications; 1:N classification for OpportunityCategories and Opportunities; and N:M junction mappings for SavedOpportunities and Applications.",
        "mermaid": """erDiagram
    USERS ||--|| STUDENT_PROFILES : "has (1:1)"
    STUDENT_PROFILES ||--o{ STUDENT_SKILLS : "possesses (1:N)"
    SKILLS ||--o{ STUDENT_SKILLS : "categorizes (1:N)"
    STUDENT_PROFILES ||--o{ STUDENT_PROJECTS : "builds (1:N)"
    STUDENT_PROFILES ||--o{ STUDENT_CERTIFICATIONS : "earns (1:N)"
    STUDENT_PROFILES ||--o{ CAREER_ANALYSES : "records (1:N)"
    STUDENT_PROFILES ||--o{ CAREER_ROADMAPS : "tracks (1:N)"
    CAREER_ROADMAPS ||--|{ ROADMAP_MILESTONES : "contains 7 stages (1:N)"
    STUDENT_PROFILES ||--o{ RESUMES : "drafts (1:N)"
    STUDENT_PROFILES ||--o{ APPLICATIONS : "submits (1:N)"
    STUDENT_PROFILES ||--o{ SAVED_OPPORTUNITIES : "bookmarks (1:N)"
    OPPORTUNITY_CATEGORIES ||--o{ OPPORTUNITIES : "classifies (1:N)"
    OPPORTUNITIES ||--o{ SAVED_OPPORTUNITIES : "bookmarked in (1:N)"
    OPPORTUNITIES ||--o{ APPLICATIONS : "applied for (1:N)"

    USERS {
        int id PK "Auto Increment"
        string email UK "VARCHAR(120), Indexed"
        string password_hash "VARCHAR(255)"
        string role "VARCHAR(20), student|admin"
        boolean is_active "DEFAULT true"
        datetime created_at "DEFAULT UTC"
    }

    STUDENT_PROFILES {
        int id PK "Auto Increment"
        int user_id FK,UK "CASCADE DELETE"
        string full_name "VARCHAR(150)"
        string headline "VARCHAR(255)"
        string college_name "VARCHAR(200)"
        string degree "VARCHAR(100)"
        string branch "VARCHAR(100)"
        float cgpa "FLOAT"
        string career_goal "VARCHAR(255)"
        string target_role "VARCHAR(150)"
        int profile_completion_pct "DEFAULT 0"
        datetime created_at "DEFAULT UTC"
    }

    SKILLS {
        int id PK "Auto Increment"
        string name UK "VARCHAR(100), Indexed"
        string category "VARCHAR(50)"
    }

    STUDENT_SKILLS {
        int id PK "Auto Increment"
        int student_id FK "CASCADE DELETE"
        int skill_id FK "SET NULL"
        string skill_name "VARCHAR(100)"
        string proficiency_level "beg|inter|adv|expert"
        float years_of_experience "FLOAT"
    }

    OPPORTUNITY_CATEGORIES {
        int id PK "Auto Increment"
        string name UK "VARCHAR(100)"
        string slug UK "VARCHAR(100)"
        string icon "VARCHAR(50)"
    }

    OPPORTUNITIES {
        int id PK "Auto Increment"
        int category_id FK "SET NULL"
        string title "VARCHAR(255), Indexed"
        string company_name "VARCHAR(200)"
        string opportunity_type "VARCHAR(50)"
        text description "TEXT"
        string event_mode "Online|Offline|Hybrid|Remote"
        string registration_fee "VARCHAR(100)"
        datetime deadline "DATETIME, Nullable"
        text required_skills_json "TEXT"
        string status "active|closed|draft"
    }

    SAVED_OPPORTUNITIES {
        int id PK "Auto Increment"
        int student_id FK "CASCADE DELETE"
        int opportunity_id FK "CASCADE DELETE"
        datetime saved_at "DEFAULT UTC"
    }

    CAREER_ANALYSES {
        int id PK "Auto Increment"
        int student_id FK "CASCADE DELETE"
        int readiness_score "INTEGER (0 to 100)"
        text strengths_json "TEXT"
        text skill_gaps_json "TEXT"
        text recommended_roles_json "TEXT"
        text ai_summary "TEXT"
        datetime created_at "DEFAULT UTC"
    }

    CAREER_ROADMAPS {
        int id PK "Auto Increment"
        int student_id FK "CASCADE DELETE"
        string target_role "VARCHAR(150)"
        int overall_progress "INTEGER (0 to 100)"
    }

    ROADMAP_MILESTONES {
        int id PK "Auto Increment"
        int roadmap_id FK "CASCADE DELETE"
        int stage_number "INTEGER (1 to 7)"
        string stage_name "VARCHAR(100)"
        string title "VARCHAR(255)"
        text action_items_json "TEXT"
        text resources_json "TEXT"
        boolean is_completed "DEFAULT false"
    }

    RESUMES {
        int id PK "Auto Increment"
        int student_id FK "CASCADE DELETE"
        string title "VARCHAR(150)"
        string template_name "modern|classic"
        int ats_score "INTEGER (0 to 100)"
        text content_data_json "TEXT"
    }

    APPLICATIONS {
        int id PK "Auto Increment"
        int student_id FK "CASCADE DELETE"
        int opportunity_id FK "SET NULL"
        string company_name "VARCHAR(150)"
        string position_title "VARCHAR(150)"
        string status "applied|in_progress|interview|offer|rejected"
        date applied_date "DATE"
    }"""
    },
    {
        "id": "5a_rec_pipeline",
        "title": "5.1 Hybrid Career Opportunity Recommendation Pipeline",
        "figure_no": "Figure 5.1",
        "caption": "Two-Stage Multi-Facet SQL Pre-Filtering and 4-Factor AI Semantic Match Scoring Pipeline",
        "desc": "The recommendation pipeline processes candidate listings through 5 sequential stages: (1) Multi-Facet SQL pre-filtering eliminating expired/inactive listings; (2) Student DNA vector extraction and normalization; (3) 4-Factor weighted fit scoring combining Skill Overlap (45%), Goal Alignment (30%), Academic Eligibility (15%), and Experience Depth (10%); (4) Natural language explainability rationale and preparation tips generation; (5) Post-scoring filtering and multi-criteria sorting stream.",
        "mermaid": """flowchart TD
    START(["🚀 Student Requests Opportunities Feed\n(Filters: Type, Category, Mode, Fee, Search Query)"])

    subgraph STAGE1 ["Stage 1: Multi-Facet SQL Pre-Filtering"]
        Q1["Fetch Active Opportunities (status='active' AND deadline >= NOW())"]
        Q2["Apply Opportunity Type Filter (Internship, Job, Hackathon, Course, Cert, Comp)"]
        Q3["Apply Mode & Remote Flags (Online, Offline, Hybrid, Remote)"]
        Q4["Apply Fee Filter (Free vs Paid) & Location Substring Match"]
        Q5["Smart Multi-Field Keyword Search (Title, Company, Description, Required Skills)"]
        Q1 --> Q2 --> Q3 --> Q4 --> Q5
    end

    subgraph STAGE2 ["Stage 2: Student DNA Vector Normalization"]
        V1["Extract Student Profile (Verified Skills, Target Role, Career Goal)"]
        V2["Extract Academic Vector (Degree, Branch, CGPA, Graduation Year)"]
        V3["Extract Experience Vector (Project Count, Accredited Certifications)"]
        V1 --> V2 --> V3
    end

    subgraph STAGE3 ["Stage 3: 4-Factor DNA Weighted Scoring Algorithm"]
        direction TB
        F1["Factor 1: Skill Overlap & Semantic Match (45% Weight)\nOverlap Ratio = Matched Skills / Total Required Skills"]
        F2["Factor 2: Career Goal & Role Alignment (30% Weight)\nTarget Title Match vs Opportunity Title/Description"]
        F3["Factor 3: Academic & Eligibility Fit (15% Weight)\nDegree Alignment & CGPA Threshold Checks"]
        F4["Factor 4: Experience & Project Depth (10% Weight)\nHands-on Capstone Projects + Certifications Count"]

        SCORE["Total Match Score (0 - 100%)\nTotal = (F1 × 45) + (F2 × 30) + (F3 × 15) + (F4 × 10)"]
        F1 --> SCORE
        F2 --> SCORE
        F3 --> SCORE
        F4 --> SCORE
    end

    subgraph STAGE4 ["Stage 4: AI Explainability & Preparation Diagnostics"]
        E1["Identify Matched Skills (Green Badges)"]
        E2["Detect Missing Skills (Red Gap Badges)"]
        E3["Generate Natural Language 'Why Recommended' Rationale"]
        E4["Generate Tailored Preparation Tips (Hackathon pitch, STAR drills, Docs study)"]
        E1 --> E2 --> E3 --> E4
    end

    subgraph STAGE5 ["Stage 5: Post-Filter & Sorting Stream"]
        P1{"Match Score >= min_match Filter?"}
        P2{"Skills Chip Tag Match?"}
        P3{"Urgent Deadline (< 7 Days)?"}
        SORT["Sort By: Match Desc / Deadline Asc / Newest / Title Asc"]
        P1 -- Yes --> P2 -- Yes --> P3 -- Yes --> SORT
        P1 -- No --> DROP["Discard Item"]
        P2 -- No --> DROP
        P3 -- No --> DROP
    end

    FINAL(["📦 Return Ranked JSON Feed to Client Browser\n(Render Opportunity Cards with Match Dial & Diagnostics)"])

    START --> STAGE1
    START --> STAGE2
    STAGE1 --> STAGE3
    STAGE2 --> STAGE3
    STAGE3 --> STAGE4
    STAGE4 --> STAGE5
    SORT --> FINAL"""
    },
    {
        "id": "5b_career_analysis_flow",
        "title": "5.2 AI Career Analysis & Readiness Diagnostic Workflow",
        "figure_no": "Figure 5.2",
        "caption": "AI Career Readiness Diagnostic Flow with Multi-Model Fallback and Radar Rendering",
        "desc": "Details how student academic and skill credentials are formatted into structured prompts sent to Google Gemini LLM. Includes multi-model waterfall execution (gemini-2.5-flash -> 2.0 -> 1.5), 10-second timeout safeguarding, defensive JSON parsing, deterministic heuristic calculation fallback, database persistence, and Chart.js competency radar visualization.",
        "mermaid": """flowchart TD
    A(["🎓 Student Requests AI Career Audit"]) --> B["Gather Profile Data:\nFull Name, Degree, Branch, CGPA, Target Role,\nSkills Array, Projects Tech Stack, Certifications"]
    B --> C["Construct Structured Gemini Prompt\n(Enforce Strict-JSON Schema & System Rules)"]
    C --> D{"GEMINI_API_KEY Configured?"}
    D -- Yes --> E["Invoke Gemini GenerativeModel\n(gemini-2.5-flash -> 2.0 -> 1.5)\nwith 10-Second Strict Timeout"]
    E --> F{"Response Valid within 10s?"}
    F -- Yes --> G["Clean Markdown Fences & Parse JSON\n(_clean_and_parse_json)"]
    G --> H{"Valid JSON with readiness_score?"}
    H -- Yes --> I["Structured AI Diagnosis Payload"]
    H -- No --> J["Activate High-Fidelity Heuristic Fallback Engine"]
    F -- No (Timeout / Error) --> J
    D -- No --> J
    J --> K["Algorithmic Scoring Matrix:\n• Base Score (45) + Skills (+25 max)\n• Projects (+20 max) + Certs (+10 max) + CGPA (+10 max)\n• Dynamic Role-Based Skill Gap Mapping"]
    K --> I
    I --> L["Persist Record in career_analyses Table:\n• readiness_score (0-100)\n• strengths_json, weaknesses_json, skill_gaps_json\n• recommended_roles_json, recommended_technologies_json\n• ai_summary text"]
    L --> M["Frontend Visual Presentation:\n1. Circular Readiness Score Gauge\n2. Chart.js Competency Radar Chart\n3. Strengths vs Growth Area Cards\n4. Recommended Learning Stacks"]
    M --> N(["🏁 Audit Complete & Dashboard Synchronized"])"""
    },
    {
        "id": "5c_roadmap_timeline",
        "title": "5.3 Career Roadmap Timeline & 7-Stage Progression Flow",
        "figure_no": "Figure 5.3",
        "caption": "7-Stage Chronological Career Roadmap Milestone Timeline & Mathematical Progress Model",
        "desc": "Models the 7 chronologically sequenced career preparation stages: (1) Current Skill Assessment, (2) Skills to Learn, (3) Projects to Build, (4) Certifications to Earn, (5) Internship Preparation, (6) Interview Preparation, and (7) Placement Preparation. Each stage encapsulates concrete actionable tasks and verified educational platform URLs. Overall progress is calculated mathematically: Progress % = (Sum of Stage Scores / 7) * 100.",
        "mermaid": """flowchart TD
    subgraph STAGE_1 ["Stage 1: Current Skill Assessment (Month 0 - 1)"]
        S1["🔍 Technical Audit & Benchmark Baseline\n• Action: Timed DSA & problem-solving diagnostic\n• Action: Audit GitHub repositories for commit hygiene\n• Action: Document target role skill gaps\n• Resources: LeetCode Top 150, Roadmap.sh, HackerRank"]
    end

    subgraph STAGE_2 ["Stage 2: Skills to Learn (Month 1 - 2)"]
        S2["📚 Master Role-Specific Core Competencies\n• Full-Stack: Modern JS/React, Python/FastAPI, SQL optimization\n• AI/ML: NumPy, Pandas, Scikit-Learn, PyTorch, Model Serving\n• DevOps: Linux CLI, Docker, Kubernetes, Terraform IaC\n• Resources: MDN Docs, Python Docs, W3Schools SQL, React.dev"]
    end

    subgraph STAGE_3 ["Stage 3: Projects to Build (Month 2 - 3)"]
        S3["💻 Flagship Capstone Production Application\n• Action: Build end-to-end full-stack app with JWT & DB caching\n• Action: Write unit/integration tests with >80% coverage\n• Action: Deploy live on AWS/Vercel/Render with Docker CI/CD\n• Resources: Docker Docs, GitHub Skills, Codecrafters"]
    end

    subgraph STAGE_4 ["Stage 4: Certifications to Earn (Month 3 - 4)"]
        S4["🏆 Industry-Recognized Credential Validation\n• Action: Enroll and clear vendor certification (AWS / Meta / Google)\n• Action: Publish verified credential badge on LinkedIn & Resume\n• Resources: AWS Skill Builder, Meta Professional, CNCF CKA"]
    end

    subgraph STAGE_5 ["Stage 5: Internship Preparation (Month 4 - 5)"]
        S5["🎯 Targeted Outreach & Application Sprint\n• Action: Tailor AI resume bullets with quantified action verbs\n• Action: Apply to 15+ curated listings in OPPORA AI Tracker\n• Action: Connect with 10+ industry alumni for warm referrals\n• Resources: LinkedIn Student Guide, GitHub Student Pack"]
    end

    subgraph STAGE_6 ["Stage 6: Interview Preparation (Month 5 - 6)"]
        S6["⚔️ Technical Coding & Behavioral STAR Drills\n• Action: Solve 75+ medium LeetCode interview patterns\n• Action: Conduct 3 peer mock technical rounds on Pramp\n• Action: Draft STAR responses for behavioral leadership questions\n• Resources: Tech Interview Handbook, System Design Primer, NeetCode"]
    end

    subgraph STAGE_7 ["Stage 7: Placement Preparation (Month 6+)"]
        S7["🎉 Offer Evaluation, Compensation & Day-1 Success\n• Action: Review offer letters, stipend structures & benefits\n• Action: Master git branching & large codebase onboarding\n• Resources: Levels.fyi Tech Salaries, Interviewing.io"]
    end

    STAGE_1 --> STAGE_2 --> STAGE_3 --> STAGE_4 --> STAGE_5 --> STAGE_6 --> STAGE_7

    subgraph PROGRESS_ENGINE ["📈 Dynamic Progress Tracking Formula"]
        P_MATH["Overall Progress % = (Σ Stage Scores / 7) × 100\nWhere Stage Score = 1.0 (if marked complete) OR (Completed Actions / Total Actions in Stage)"]
    end

    STAGE_7 -.-> PROGRESS_ENGINE"""
    },
    {
        "id": "5d_resume_pdf_pipeline",
        "title": "5.4 AI Resume Builder → PDF Generation Pipeline",
        "figure_no": "Figure 5.4",
        "caption": "Split-Screen Resume Editor, Gemini ATS Enhancer, and ReportLab PDF Generation Flow",
        "desc": "Ingests student profile credentials, provides interactive split-screen document editing, triggers Gemini action-verb bullet refinement and ATS keyword density diagnostics, persists snapshots to MySQL, and renders binary PDF streams via ReportLab 5.0 (supporting Modern Tech and Classic Corporate templates) without intermediate temporary files.",
        "mermaid": """flowchart LR
    subgraph INPUT_STAGE ["1. Data Aggregation & Intake"]
        IN1["StudentProfile DB Record\n(Academics, Degree, CGPA, College)"]
        IN2["Skills & Projects Collections"]
        IN3["Manual User Customizations\n(Custom Title, Objective, Experience)"]
        IN1 --> MERGE["Merged Resume Object"]
        IN2 --> MERGE
        IN3 --> MERGE
    end

    subgraph AI_STAGE ["2. AI Enhancement & ATS Diagnostic"]
        direction TB
        MERGE --> AI_ENHANCE["Gemini Bullet Enhancer\n• Ingest raw passive bullet\n• Rewrite with dynamic action verbs\n• Quantify impact & metrics (% / latency)"]
        MERGE --> ATS_SCAN["Gemini ATS Scorer\n• Scan keywords against Target Role\n• Calculate ATS Score (0 - 100)\n• Output formatting & keyword suggestions"]
    end

    subgraph PERSIST_STAGE ["3. Persistence & Snapshot"]
        AI_ENHANCE --> DB_SAVE["Save Resume Draft in resumes Table\n(content_data_json & ats_score)"]
        ATS_SCAN --> DB_SAVE
    end

    subgraph PDF_ENGINE ["4. ReportLab 5.0 PDF Service Pipeline"]
        direction TB
        DB_SAVE --> TEMPLATE_CHOICE{"Template Selected?"}
        TEMPLATE_CHOICE -- "Modern" --> MOD["_build_modern_resume()\n• Primary: Deep Navy (#1E3A8A)\n• Secondary: Royal Blue (#2563EB)\n• Two-Column Key Details Table\n• Crisp Horizontal Dividers"]
        TEMPLATE_CHOICE -- "Classic" --> CLA["_build_classic_resume()\n• Primary: Slate Black (#0F172A)\n• Traditional Academic Layout\n• Clean Minimalist Dividers"]
        MOD --> BUILD["SimpleDocTemplate.build(elements)\n• 36pt Uniform Margins\n• Standard Letter Page Size\n• Flowable Paragraphs & Spacers"]
        CLA --> BUILD
        BUILD --> BUFFER["BytesIO In-Memory Buffer (seek to 0)"]
    end

    subgraph OUTPUT_STAGE ["5. Client Delivery"]
        BUFFER --> STREAM["Flask send_file / Response Stream\n• Content-Type: application/pdf\n• Attachment Header: student_resume.pdf"]
        STREAM --> DOWNLOAD(["📥 Browser Downloads High-Fidelity PDF Resume"])
    end"""
    },
    {
        "id": "5e_kanban_flow",
        "title": "5.5 Application Tracking Kanban State Machine Flow",
        "figure_no": "Figure 5.5",
        "caption": "Finite State Machine Workflow for 5-Column Kanban Recruitment Lifecycle",
        "desc": "Models the 5 lifecycle states of job and internship applications: Applied -> In Progress -> Interview Scheduled -> Offer Received or Rejected -> Archived. Card movements trigger immediate REST calls updating status timestamps and recalculating conversion rates (Interview Rate % and Offer Success Rate %).",
        "mermaid": """stateDiagram-v2
    [*] --> Applied: 1. Student applies to Opportunity or Adds Card manually

    Applied --> InProgress: 2. Recruiter views profile / Coding OA assigned
    Applied --> Rejected: Instant rejection / Screen fail

    InProgress --> InterviewScheduled: 3. Technical / HR Interview scheduled (Store datetime)
    InProgress --> Rejected: Did not clear OA

    InterviewScheduled --> OfferReceived: 4. Candidate clears all rounds & receives Offer Letter!
    InterviewScheduled --> Rejected: Post-interview rejection

    OfferReceived --> Archived: 5. Offer Accepted / Placement finalized
    Rejected --> Archived: 6. Opportunity closed / Stored for historical analytics

    state Applied {
        [*] --> InReview
        InReview --> ApplicationLogged
    }

    state InterviewScheduled {
        [*] --> Round1_Technical
        Round1_Technical --> Round2_SystemDesign
        Round2_SystemDesign --> Round3_BehavioralHR
    }

    state OfferReceived {
        [*] --> OfferLetterEvaluation
        OfferLetterEvaluation --> CompensationReview
    }

    note right of OfferReceived
        Metrics Impact:
        • Total Applications incremented
        • Interview Conversion Rate % updated
        • Offer Success Rate % calculated
    end note"""
    }
]

def fetch_mermaid_png(mermaid_code, output_path):
    """Fetches rendered PNG from mermaid.ink API with defensive fallback."""
    try:
        graph_bytes = mermaid_code.encode('utf-8')
        base64_str = base64.urlsafe_b64encode(graph_bytes).decode('ascii')
        url = f"https://mermaid.ink/img/{base64_str}?bgColor=!white"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read()
            if len(content) > 500:
                with open(output_path, "wb") as f:
                    f.write(content)
                print(f"Successfully fetched: {os.path.basename(output_path)} ({len(content)} bytes)")
                return True
    except Exception as e:
        print(f"Warning: Could not fetch mermaid image for {os.path.basename(output_path)}: {e}")
    return False

def set_cell_background(cell, fill_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_color}"/>')
    tcPr.append(shd)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideV w:val="none"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)

def render_all_diagrams():
    """Renders all Mermaid diagrams to PNG via mermaid.ink."""
    print("=== RENDERING MERMAID DIAGRAMS TO PNG ===")
    rendered_map = {}
    for item in DIAGRAMS_DATA:
        diag_id = item["id"]
        png_path = os.path.join(DIAGRAMS_DIR, f"{diag_id}.png")
        if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
            print(f"Already cached: {diag_id}.png")
            rendered_map[diag_id] = png_path
            continue
        
        success = fetch_mermaid_png(item["mermaid"], png_path)
        if success and os.path.exists(png_path):
            rendered_map[diag_id] = png_path
        else:
            print(f"Skipping image embed for {diag_id}, will render text representation.")
    return rendered_map

def build_word_document(rendered_map):
    """Builds the comprehensive Word document containing all diagrams."""
    print("=== BUILDING WORD DOCUMENT ===")
    doc = docx.Document()

    # A4 Page Setup
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Styles
    styles = doc.styles
    normal_style = styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # ================= TITLE PAGE =================
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(18)
    run_title = p_title.add_run("CAREER DNA AI (OPPORA AI)\nCOMPLETE ARCHITECTURAL, UML, DFD, ER & AI SYSTEM DIAGRAMS\n")
    run_title.bold = True
    run_title.font.size = Pt(18)
    run_title.font.name = 'Times New Roman'
    run_title.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(30)
    run_sub = p_sub.add_run("A Comprehensive Technical Architecture & Design Reference Document\nPrepared for Academic Report, Viva-Voce Examination & Project Presentation\n")
    run_sub.font.size = Pt(13)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(40)
    run_meta = p_meta.add_run("Project Name: OPPORA AI\nFramework: Python Flask 3.0 • MySQL 8.0 • Google Gemini AI • ReportLab 5.0\nCandidate: BAVASREE S (Reg No: 713521104001)\nDepartment of Computer Science and Engineering\nSNS College of Technology, Coimbatore — 641 035\nMarch 2026\n")
    run_meta.font.size = Pt(12)
    run_meta.font.name = 'Times New Roman'

    doc.add_page_break()

    # ================= TABLE OF CONTENTS =================
    p_toc_head = doc.add_paragraph()
    run_toc_head = p_toc_head.add_run("TABLE OF DIAGRAMS & SYSTEM FIGURES\n")
    run_toc_head.bold = True
    run_toc_head.font.size = Pt(15)
    run_toc_head.font.color.rgb = RGBColor(30, 58, 138)

    table_toc = doc.add_table(rows=1, cols=3)
    table_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_toc)
    hdr_cells = table_toc.rows[0].cells
    hdr_cells[0].text = "S.No."
    hdr_cells[1].text = "Diagram / Figure Title"
    hdr_cells[2].text = "Category"
    for c in hdr_cells:
        set_cell_background(c, "E2E8F0")
        for p in c.paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(11)

    for idx, d in enumerate(DIAGRAMS_DATA):
        row_cells = table_toc.add_row().cells
        row_cells[0].text = str(idx + 1)
        row_cells[1].text = d["title"]
        category = d["id"].split("_")[1].upper()
        row_cells[2].text = category
        for c in row_cells:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10.5)

    doc.add_page_break()

    # ================= DIAGRAM CHAPTERS =================
    for idx, d in enumerate(DIAGRAMS_DATA):
        diag_id = d["id"]
        
        # Section Header
        p_sec = doc.add_paragraph()
        p_sec.paragraph_format.space_before = Pt(16)
        p_sec.paragraph_format.space_after = Pt(6)
        run_sec = p_sec.add_run(d["title"])
        run_sec.bold = True
        run_sec.font.size = Pt(14)
        run_sec.font.color.rgb = RGBColor(30, 58, 138)

        # Description
        p_desc = doc.add_paragraph()
        p_desc.paragraph_format.space_after = Pt(10)
        r_desc = p_desc.add_run(d["desc"])
        r_desc.font.size = Pt(11)

        # Embed Image if available
        png_path = rendered_map.get(diag_id)
        if png_path and os.path.exists(png_path):
            try:
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(8)
                p_img.paragraph_format.space_after = Pt(6)
                
                # Check aspect ratio
                run_img = p_img.add_run()
                run_img.add_picture(png_path, width=Inches(6.25))
            except Exception as ex:
                print(f"Image insert error for {diag_id}: {ex}")

        # Caption
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(14)
        r_cap = p_cap.add_run(f"{d['figure_no']}: {d['caption']}")
        r_cap.bold = True
        r_cap.font.italic = True
        r_cap.font.size = Pt(10.5)
        r_cap.font.color.rgb = RGBColor(51, 65, 85)

        # Technical Box with Mermaid Spec
        p_box_hdr = doc.add_paragraph()
        p_box_hdr.paragraph_format.space_before = Pt(6)
        p_box_hdr.paragraph_format.space_after = Pt(2)
        r_box_hdr = p_box_hdr.add_run("Formal Diagram Specification (Mermaid / PlantUML Compatible Source):")
        r_box_hdr.bold = True
        r_box_hdr.font.size = Pt(10)
        r_box_hdr.font.color.rgb = RGBColor(71, 85, 105)

        tbl_code = doc.add_table(rows=1, cols=1)
        tbl_code.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl_code, color="CBD5E1", sz="4", val="single")
        cell = tbl_code.rows[0].cells[0]
        set_cell_background(cell, "F8FAFC")
        p_code = cell.paragraphs[0]
        p_code.paragraph_format.space_before = Pt(4)
        p_code.paragraph_format.space_after = Pt(4)
        r_code = p_code.add_run(d["mermaid"])
        r_code.font.name = "Consolas"
        r_code.font.size = Pt(8.5)
        r_code.font.color.rgb = RGBColor(30, 41, 59)

        doc.add_page_break()

    # Save documents
    out_docx_1 = os.path.join(os.path.dirname(__file__), "OPPORA_AI_Project_Report_Diagrams.docx")
    out_docx_2 = os.path.join(os.path.dirname(__file__), "OPPORA_AI_Project_Report.docx")
    
    doc.save(out_docx_1)
    print(f"Successfully created: {out_docx_1}")
    doc.save(out_docx_2)
    print("All OPPORA AI Word document copies synchronized successfully!")

if __name__ == "__main__":
    rendered = render_all_diagrams()
    build_word_document(rendered)
