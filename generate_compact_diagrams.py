import os
import sys
import base64
import time
import urllib.request
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIAGRAMS_DIR = os.path.join(BASE_DIR, "diagram_images", "compact")
os.makedirs(DIAGRAMS_DIR, exist_ok=True)

DIAGRAMS_DATA = [
    {
        "num": 1,
        "id": "1_system_architecture",
        "title": "System Architecture Diagram",
        "figure_no": "Figure 1",
        "caption": "Figure 1: Four-Tier System Architecture Diagram of OPPORA AI",
        "desc": "The OPPORA AI system follows a decoupled 4-tier architecture comprising Presentation Layer, API & Security Layer, Core Services Layer, and Database & External AI Layer.",
        "components": [
            ("Presentation Layer", "Responsive Web UI built with HTML5, CSS3, and JavaScript dashboard."),
            ("API & Security Layer", "Flask REST API with JWT-based authentication and route guards."),
            ("Core Services Layer", "Gemini AI Service, 4-Factor Recommendation Engine, and ReportLab PDF Service."),
            ("Data & External Layer", "MySQL 8.0 Relational Database and Google Gemini Generative AI endpoints.")
        ],
        "mermaid": """flowchart TD
    subgraph PRESENTATION ["1. Presentation Layer"]
        UI["Web Interface\\n(HTML5, CSS, JS Dashboard)"]
    end

    subgraph API_LAYER ["2. API & Security Layer"]
        API["Flask REST API & JWT Auth"]
    end

    subgraph SERVICE_LAYER ["3. Core Services Layer"]
        AI_SVC["Gemini AI Service\\n(Career & Gap Audit)"]
        REC_SVC["Recommendation Engine\\n(Opportunity Matcher)"]
        PDF_SVC["Resume PDF Generator\\n(ReportLab Engine)"]
    end

    subgraph DATA_LAYER ["4. Database & External AI Layer"]
        DB[("MySQL Database\\n(Users, Skills, Jobs)")]
        GEMINI["Google Gemini API\\n(LLM Intelligence)"]
    end

    UI <-->|HTTP / REST Requests| API
    API --> AI_SVC
    API --> REC_SVC
    API --> PDF_SVC
    AI_SVC <-->|Prompts & Insights| GEMINI
    AI_SVC --> DB
    REC_SVC <-->|Query Listings| DB
    PDF_SVC --> DB
"""
    },
    {
        "num": 2,
        "id": "2_level_0_dfd",
        "title": "Level 0 Data Flow Diagram (Context DFD)",
        "figure_no": "Figure 2",
        "caption": "Figure 2: Level 0 Context Data Flow Diagram for OPPORA AI",
        "desc": "The Level 0 Context Diagram defines the external boundaries of OPPORA AI, showing data interactions between Students, Administrators, the central system, and Google Gemini AI.",
        "components": [
            ("Student", "Provides profile details, skills, and resume data; receives readiness scores, recommendations, and PDF resumes."),
            ("Administrator", "Manages opportunity listings and inspects platform analytics."),
            ("OPPORA AI System", "Central processing engine managing business rules, data storage, and workflows."),
            ("Google Gemini AI", "Receives prompt contexts and returns AI evaluation and roadmap insights.")
        ],
        "mermaid": """flowchart LR
    STUDENT(["Student"])
    ADMIN(["Administrator"])
    GEMINI(["Google Gemini AI"])
    
    SYSTEM[["0.0\\nOPPORA AI System\\n(Career Guidance Platform)"]]

    STUDENT -->|Profile, Skills & Resume Data| SYSTEM
    SYSTEM -->|Readiness Score, Recommendations & PDF Resume| STUDENT

    ADMIN -->|Manage Opportunities & Categories| SYSTEM
    SYSTEM -->|System Reports & Analytics| ADMIN

    SYSTEM -->|Student Context & Prompts| GEMINI
    GEMINI -->|AI Analysis & Roadmap Insights| SYSTEM
"""
    },
    {
        "num": 3,
        "id": "3_level_1_dfd",
        "title": "Level 1 Data Flow Diagram",
        "figure_no": "Figure 3",
        "caption": "Figure 3: Level 1 Data Flow Diagram across Core Subsystems and Data Stores",
        "desc": "The Level 1 DFD decomposes the system into 4 key operational processes (Authentication, Profile Management, AI Analysis & Recommendations, Resume & Applications) and 3 primary relational stores.",
        "components": [
            ("1.0 User Authentication", "Validates student and admin credentials and issues signed session tokens."),
            ("2.0 Profile & Skills Management", "Performs CRUD operations on academic background, skills, and career goals."),
            ("3.0 AI Analysis & Matching", "Evaluates career readiness via Gemini AI and ranks opportunities using weighted match logic."),
            ("4.0 Resume & Applications", "Compiles ATS-friendly resumes and tracks job applications via Kanban stages."),
            ("Data Stores (D1 - D3)", "D1: Users & Profiles, D2: Opportunities Catalog, D3: Applications & Resumes.")
        ],
        "mermaid": """flowchart LR
    subgraph ENTITIES [Entities]
        ADMIN([Admin])
        STUDENT([Student])
    end

    subgraph PROCESSES [Processes]
        P1[[1.0 Authentication]]
        P2[[2.0 Profile Management]]
        P3[[3.0 AI Recommendations]]
        P4[[4.0 Resume & Applications]]
    end

    subgraph STORES [Data Stores]
        D1[(D1: Profiles)]
        D2[(D2: Opportunities)]
        GEMINI([Gemini AI])
        D3[(D3: Applications)]
    end

    ADMIN -->|Admin Login| P1
    ADMIN -->|Post Jobs| D2

    STUDENT -->|Credentials| P1
    P1 <-->|Verify| D1

    STUDENT -->|Skills & DNA| P2
    P2 <-->|Save/Load| D1

    STUDENT -->|Request Jobs| P3
    P3 <-->|Profile DNA| D1
    P3 <-->|Active Jobs| D2
    P3 <-->|Prompts| GEMINI
    P3 -->|Matches| STUDENT

    STUDENT -->|Build Resume| P4
    P4 <-->|Save Resumes| D3
    P4 -->|PDF Resume| STUDENT
"""
    },
    {
        "num": 4,
        "id": "4_level_2_dfd",
        "title": "Level 2 Data Flow Diagram (AI Analysis & Matching)",
        "figure_no": "Figure 4",
        "caption": "Figure 4: Level 2 Data Flow Diagram for AI Career Analysis & Matching Subsystem",
        "desc": "The Level 2 DFD decomposes Process 3.0 into 4 clear sequential subprocesses: Profile DNA Aggregation, Gemini AI Evaluation, Skill Gap Scoring, and 4-Factor Opportunity Ranking.",
        "components": [
            ("3.1 Profile DNA Aggregation", "Extracts validated student skills, CGPA, project history, and career ambition."),
            ("3.2 Gemini AI Career Evaluation", "Sends structured prompt context to Google Gemini to assess industry alignment."),
            ("3.3 Skill Gap & Readiness Scoring", "Calculates the 0-100% readiness score and identifies missing critical competencies."),
            ("3.4 4-Factor Opportunity Ranking", "Matches candidate competency vector against active listings and produces sorted results.")
        ],
        "mermaid": """flowchart TD
    STUDENT(["Student"])
    D1[("D1: Student Profiles")]
    D2[("D2: Opportunities Catalog")]
    GEMINI(["Google Gemini AI"])

    P3_1[["3.1 Profile DNA Aggregation\\n(Fetch Skills, CGPA, Projects)"]]
    P3_2[["3.2 Gemini AI Career Evaluation\\n(Evaluate Industry Competency)"]]
    P3_3[["3.3 Skill Gap & Readiness Scoring\\n(Compute Score 0-100% & Missing Skills)"]]
    P3_4[["3.4 4-Factor Opportunity Ranking\\n(Match Skills, Goal, CGPA, Urgency)"]]

    STUDENT -->|Trigger Career Audit| P3_1
    D1 -->|Student Profile Data| P3_1
    P3_1 -->|Structured Context| P3_2
    P3_2 <-->|Prompt Payload / AI Feedback| GEMINI
    P3_2 -->|Evaluation Results| P3_3
    P3_3 -->|Readiness Score & Gaps| STUDENT
    P3_3 -->|Competency Vector| P3_4
    D2 -->|Active Listings| P3_4
    P3_4 -->|Ranked Recommended Opportunities| STUDENT
"""
    },
    {
        "num": 5,
        "id": "5_uml_use_case",
        "title": "UML Use Case Diagram",
        "figure_no": "Figure 5",
        "caption": "Figure 5: UML Use Case Diagram for Student and Administrator Roles",
        "desc": "The UML Use Case Diagram illustrates the primary capabilities accessible by Students (profiling, AI analysis, recommendations, roadmap, resume, Kanban) and Administrators (catalog and analytics management).",
        "components": [
            ("Student Actor", "Accesses authentication, profile setup, career gap analysis, recommendations, 7-stage roadmap, resume builder, and Kanban application tracker."),
            ("Administrator Actor", "Accesses authentication, adds/updates opportunities in the catalog, and monitors platform analytics.")
        ],
        "mermaid": """flowchart LR
    STUDENT["Student"]
    ADMIN["Admin"]

    subgraph OPPORA_AI ["OPPORA AI Platform"]
        UC1(["Manage Profile & Skills"])
        UC2(["Run AI Career Gap Analysis"])
        UC3(["Explore Recommendations"])
        UC4(["Track 7-Stage Roadmap"])
        UC5(["Build & Export AI Resume"])
        UC6(["Track Applications on Kanban"])
        UC_AUTH(["User Authentication"])
        UC7(["Manage Opportunity Catalog"])
        UC8(["View System Analytics"])
    end

    STUDENT --- UC_AUTH
    STUDENT --- UC1
    STUDENT --- UC2
    STUDENT --- UC3
    STUDENT --- UC4
    STUDENT --- UC5
    STUDENT --- UC6

    ADMIN --- UC_AUTH
    ADMIN --- UC7
    ADMIN --- UC8
"""
    },
    {
        "num": 6,
        "id": "6_uml_class",
        "title": "UML Class Diagram",
        "figure_no": "Figure 6",
        "caption": "Figure 6: UML Class Diagram Representing Core Domain Entities",
        "desc": "The UML Class Diagram shows the 6 core structural classes (User, StudentProfile, Skill, Opportunity, CareerAnalysis, Application) along with their key attributes, operations, and multiplicities.",
        "components": [
            ("User", "Represents login identity and role permissions (Student / Admin)."),
            ("StudentProfile", "Holds academic details, CGPA, target career goal, and profile completeness."),
            ("Skill", "Maintains specific competencies linked to student profiles with proficiency levels."),
            ("Opportunity", "Encapsulates jobs, internships, or hackathons with eligibility criteria."),
            ("CareerAnalysis", "Stores calculated readiness percentage and identified skill deficits."),
            ("Application", "Tracks candidate job submissions through Kanban stages.")
        ],
        "mermaid": """classDiagram
    class User {
        +int user_id
        +string email
        +string password_hash
        +string role
        +login()
        +register()
    }

    class StudentProfile {
        +int profile_id
        +int user_id
        +string full_name
        +float cgpa
        +string career_goal
        +updateProfile()
    }

    class Skill {
        +int skill_id
        +int profile_id
        +string skill_name
        +string proficiency
    }

    class Opportunity {
        +int opp_id
        +string title
        +string company
        +string required_skills
        +string type
        +checkEligibility()
    }

    class CareerAnalysis {
        +int analysis_id
        +int profile_id
        +float readiness_score
        +string missing_skills
        +runAnalysis()
    }

    class Application {
        +int app_id
        +int profile_id
        +int opp_id
        +string status
        +updateStatus()
    }

    User "1" --> "1" StudentProfile : has
    StudentProfile "1" --> "*" Skill : possesses
    StudentProfile "1" --> "*" CareerAnalysis : receives
    StudentProfile "1" --> "*" Application : submits
    Opportunity "1" <-- "*" Application : relates_to
"""
    },
    {
        "num": 7,
        "id": "7_uml_sequence",
        "title": "UML Sequence Diagram",
        "figure_no": "Figure 7",
        "caption": "Figure 7: UML Sequence Diagram for Career Analysis and Opportunity Matching",
        "desc": "The UML Sequence Diagram models the chronological message exchange between Student, Web Portal, Flask API, Gemini AI Service, and MySQL Database during career analysis.",
        "components": [
            ("Step 1 - 2", "Student initiates career analysis; Web Portal dispatches POST request."),
            ("Step 3 - 4", "Flask API reads stored profile DNA and skills from MySQL Database."),
            ("Step 5 - 6", "Flask API calls Gemini AI Service to compute readiness score and identify gaps."),
            ("Step 7 - 8", "API saves analysis and queries matching qualified opportunities."),
            ("Step 9 - 10", "API returns payload to UI; Web Portal displays radar charts and matched jobs.")
        ],
        "mermaid": """sequenceDiagram
    autonumber
    actor Student
    participant WebUI as Web Interface
    participant FlaskAPI as Flask API
    participant Gemini as Gemini AI Service
    participant DB as MySQL Database

    Student->>WebUI: Click 'Analyze Career Readiness'
    WebUI->>FlaskAPI: POST /api/career-analysis
    FlaskAPI->>DB: Fetch Student Profile & Skills
    DB-->>FlaskAPI: Return Profile Record
    FlaskAPI->>Gemini: Send Profile Context Prompt
    Gemini-->>FlaskAPI: Return Readiness Score & Skill Gaps
    FlaskAPI->>DB: Save Analysis Record
    FlaskAPI->>DB: Query Matching Opportunities
    DB-->>FlaskAPI: Return Filtered Listings
    FlaskAPI-->>WebUI: Return Analysis JSON & Top Matches
    WebUI-->>Student: Display Readiness Score, Radar & Opportunities
"""
    },
    {
        "num": 8,
        "id": "8_er_diagram",
        "title": "Entity Relationship (ER) Diagram",
        "figure_no": "Figure 8",
        "caption": "Figure 8: Entity Relationship Diagram of OPPORA AI Relational Database",
        "desc": "The ER Diagram illustrates the primary entities, attributes, primary/foreign keys, and cardinalities supporting the OPPORA AI persistence tier.",
        "components": [
            ("USERS & STUDENT_PROFILES", "One-to-One relationship mapping auth credentials to student details."),
            ("STUDENT_PROFILES & SKILLS", "One-to-Many relationship maintaining individual student competencies."),
            ("CAREER_ANALYSES", "Stores readiness metrics and missing skill lists linked to profiles."),
            ("OPPORTUNITIES & APPLICATIONS", "Many-to-One relationships tracking candidate job applications."),
            ("RESUMES", "Stores tailored resume drafts and ATS match scores per user.")
        ],
        "mermaid": """erDiagram
    USERS ||--o| STUDENT_PROFILES : has
    STUDENT_PROFILES ||--o{ SKILLS : possesses
    STUDENT_PROFILES ||--o{ CAREER_ANALYSES : generates
    STUDENT_PROFILES ||--o{ APPLICATIONS : submits
    OPPORTUNITIES ||--o{ APPLICATIONS : receives
    USERS ||--o{ RESUMES : creates

    USERS {
        int user_id PK
        string email
        string password_hash
        string role
    }

    STUDENT_PROFILES {
        int profile_id PK
        int user_id FK
        string full_name
        float cgpa
        string career_goal
    }

    SKILLS {
        int skill_id PK
        int profile_id FK
        string skill_name
        string proficiency
    }

    OPPORTUNITIES {
        int opp_id PK
        string title
        string company
        string category
        date deadline
    }

    CAREER_ANALYSES {
        int analysis_id PK
        int profile_id FK
        float readiness_score
        string missing_skills
    }

    APPLICATIONS {
        int app_id PK
        int profile_id FK
        int opp_id FK
        string status
        date applied_date
    }

    RESUMES {
        int resume_id PK
        int user_id FK
        string target_role
        float ats_score
    }
"""
    },
    {
        "num": 9,
        "id": "9_rec_pipeline",
        "title": "Hybrid Career Opportunity Recommendation Pipeline",
        "figure_no": "Figure 9",
        "caption": "Figure 9: Multi-Stage Hybrid Opportunity Recommendation Pipeline",
        "desc": "The Recommendation Pipeline filters, scores, and ranks opportunities using a 4-factor hybrid formula (Skills 45%, Goal 30%, CGPA 15%, Experience 10%) combined with deadline urgency sorting.",
        "components": [
            ("Stage 1: Pre-Filtering", "Eliminates expired, inactive, or non-matching category listings."),
            ("Stage 2: Content Matching", "Calculates keyword overlap between student skills and job requirements."),
            ("Stage 3: 4-Factor Scoring", "Applies weighted multi-factor formula to generate an exact match percentage."),
            ("Stage 4 - 5: Output Feed", "Sorts by score and upcoming deadlines, presenting top recommendations to the student.")
        ],
        "mermaid": """flowchart TD
    A["1. Active Listings Filter\\nFilter by active status, category & deadline"] --> B["2. Content-Based Matching\\nCompute keyword overlap with student skills"]
    B --> C["3. 4-Factor Weighted Scoring\\n• Skills Match: 45%\\n• Career Goal Fit: 30%\\n• CGPA / Academic Fit: 15%\\n• Projects / Experience: 10%"]
    C --> D["4. Ranking & Urgency Sort\\nPrioritize highest match score & upcoming deadlines"]
    D --> E["5. Recommended Opportunities Feed\\nPersonalized internships, jobs & hackathons"]
"""
    },
    {
        "num": 10,
        "id": "10_career_analysis_workflow",
        "title": "AI Career Analysis Workflow",
        "figure_no": "Figure 10",
        "caption": "Figure 10: Step-by-Step AI Career Readiness Analysis Workflow",
        "desc": "The AI Career Analysis Workflow depicts how student profile inputs are structured into an evaluation prompt, benchmarked against industry standards by Gemini AI, and returned as actionable readiness metrics.",
        "components": [
            ("Inputs & Prompting", "Aggregates academics, skills, and target career goal into structured benchmark prompts."),
            ("Gemini AI Evaluation", "LLM compares student competencies against real-world job role prerequisites."),
            ("Gap & Score Computation", "Identifies missing skills, strengths, weaknesses, and calculates readiness percentage (0-100%)."),
            ("Actionable Insights", "Outputs radar chart visualisations, milestone action items, and eligible job pathways.")
        ],
        "mermaid": """flowchart TD
    A["1. Student Profile Input\\nSkills, CGPA, Projects & Career Goal"] --> B["2. Prompt Engineering\\nBuild benchmark context for Gemini AI"]
    B --> C["3. Gemini AI Evaluation\\nCompare student competencies with industry roles"]
    C --> D["4. Gap & Readiness Diagnostics\\nIdentify missing skills, strengths & weaknesses"]
    D --> E["5. Career Readiness Score (0-100%)\\nGenerate overall score & skill radar metrics"]
    E --> F["6. Actionable Output\\nCustom roadmap milestones & recommended jobs"]
"""
    },
    {
        "num": 11,
        "id": "11_roadmap_timeline",
        "title": "Career Roadmap Timeline",
        "figure_no": "Figure 11",
        "caption": "Figure 11: 7-Stage Career Preparation Roadmap Timeline",
        "desc": "The Career Roadmap Timeline guides students across 7 progressive milestone stages, taking them from core academic fundamentals to successful placement.",
        "components": [
            ("Stage 1 - 2", "Core Foundations (computer science basics) & Technical Skill Mastery (languages/frameworks)."),
            ("Stage 3 - 4", "Portfolio Projects (deployments/GitHub) & Certifications (industry badges)."),
            ("Stage 5 - 7", "AI Resume Building (ATS polish), Interview Prep (mock tests), and Applications & Job Offers.")
        ],
        "mermaid": """flowchart LR
    S1["Stage 1\\nCore Foundations"] --> S2["Stage 2\\nSkill Mastery"]
    S2 --> S3["Stage 3\\nPortfolio Projects"]
    S3 --> S4["Stage 4\\nCertifications"]
    S4 --> S5["Stage 5\\nAI Resume Prep"]
    S5 --> S6["Stage 6\\nInterview Prep"]
    S6 --> S7["Stage 7\\nJob Applications"]
"""
    },
    {
        "num": 12,
        "id": "12_resume_pdf_pipeline",
        "title": "AI Resume Builder → PDF Generation Pipeline",
        "figure_no": "Figure 12",
        "caption": "Figure 12: AI Resume Builder to ReportLab PDF Compilation Pipeline",
        "desc": "The Resume Builder Pipeline auto-populates student credentials, applies Gemini AI to rewrite bullets with strong action verbs, audits ATS keyword density, and compiles a clean ReportLab PDF.",
        "components": [
            ("1. Auto-Import", "Populates contact info, degree, skills, and project history from profile."),
            ("2. AI Optimization", "Enhances bullet descriptions using quantified metrics and strong action verbs."),
            ("3. ATS Keyword Audit", "Compares text against target job description keywords for high parse rates."),
            ("4 - 6. PDF Compilation", "ReportLab Flowable engine renders typography and outputs a downloadable PDF.")
        ],
        "mermaid": """flowchart TD
    A["1. Auto-Import Profile Data\\nEducation, Skills, Experience & Projects"] --> B["2. Gemini AI Optimization\\nEnhance bullet points with action verbs & metrics"]
    B --> C["3. ATS Keyword Density Audit\\nVerify keyword alignment with target role"]
    C --> D["4. Template Formatting\\nApply clean ATS-friendly typography & sections"]
    D --> E["5. ReportLab PDF Generation\\nRender clean typography, margins & structure"]
    E --> F["6. Download Ready PDF Resume\\nStandard ATS-friendly resume file"]
"""
    },
    {
        "num": 13,
        "id": "13_kanban_flow",
        "title": "Application Tracking Kanban Flow",
        "figure_no": "Figure 13",
        "caption": "Figure 13: State Machine Diagram for Application Tracking Kanban Pipeline",
        "desc": "The Kanban Application Flow models the lifecycle of job applications across stages: Applied, Under Review, Interview Scheduled, Offer Received, and Rejected.",
        "components": [
            ("Applied", "Initial state created when student submits an application."),
            ("Under Review", "Candidate profile is under review by the recruiter/hiring team."),
            ("Interview Scheduled", "Student has been shortlisted for technical or HR interview rounds."),
            ("Offer Received", "Candidate has cleared all evaluation rounds and received an employment offer."),
            ("Rejected", "Application did not clear screening or interview rounds.")
        ],
        "mermaid": """stateDiagram-v2
    [*] --> Applied: Student applies for job
    Applied --> UnderReview: Recruiter reviews application
    UnderReview --> InterviewScheduled: Candidate shortlisted
    InterviewScheduled --> OfferReceived: Successfully cleared
    
    Applied --> Rejected: Not shortlisted
    UnderReview --> Rejected: Not selected
    InterviewScheduled --> Rejected: Did not clear
    
    OfferReceived --> [*]
    Rejected --> [*]
"""
    }
]

def fetch_mermaid_png(mermaid_code, output_path):
    """Fetches high-res PNG from mermaid.ink."""
    try:
        graph_bytes = mermaid_code.encode('utf-8')
        base64_str = base64.urlsafe_b64encode(graph_bytes).decode('ascii')
        url = f"https://mermaid.ink/img/{base64_str}?bgColor=!white"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            if len(content) > 500:
                with open(output_path, "wb") as f:
                    f.write(content)
                print(f"[OK] Fetched {os.path.basename(output_path)} ({len(content)} bytes)")
                return True
    except Exception as e:
        print(f"[ERROR] Failed {os.path.basename(output_path)}: {e}")
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

def generate_all():
    print("=== 1. FETCHING DIAGRAM IMAGES ===")
    rendered_map = {}
    for d in DIAGRAMS_DATA:
        diag_id = d["id"]
        png_path = os.path.join(DIAGRAMS_DIR, f"{diag_id}.png")
        if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
            print(f"[CACHED] {diag_id}.png")
            rendered_map[diag_id] = png_path
        else:
            success = fetch_mermaid_png(d["mermaid"], png_path)
            if success:
                rendered_map[diag_id] = png_path
            time.sleep(1) # courteous delay

    print("\n=== 2. CREATING WORD DOCUMENT ===")
    doc = docx.Document()

    # Standard A4 Margins
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

    # Title Page
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("OPPORA AI\nSYSTEM DESIGN & ARCHITECTURAL DIAGRAMS\n")
    r_title.bold = True
    r_title.font.size = Pt(20)
    r_title.font.name = 'Times New Roman'
    r_title.font.color.rgb = RGBColor(26, 54, 93)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(30)
    r_sub = p_sub.add_run("Official System Architecture, UML, DFD, ER & AI Pipeline Diagrams\nStandard Technical Reference for Project Report & Viva-Voce\n")
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(74, 85, 104)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(40)
    r_meta = p_meta.add_run("Project Name: OPPORA AI\nDomain: Artificial Intelligence & Career Opportunity Recommendation\nTechnology Stack: Python Flask, MySQL, Google Gemini AI, ReportLab\nDepartment of Computer Science and Engineering\nAcademic Year 2025 - 2026\n")
    r_meta.font.size = Pt(12)
    r_meta.font.name = 'Times New Roman'

    doc.add_page_break()

    # Table of Contents
    p_toc = doc.add_paragraph()
    p_toc.paragraph_format.space_before = Pt(12)
    p_toc.paragraph_format.space_after = Pt(12)
    r_toc = p_toc.add_run("LIST OF PROJECT DIAGRAMS")
    r_toc.bold = True
    r_toc.font.size = Pt(16)
    r_toc.font.color.rgb = RGBColor(26, 54, 93)

    table_toc = doc.add_table(rows=1, cols=3)
    table_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_toc)
    hdr_cells = table_toc.rows[0].cells
    hdr_cells[0].text = "S.No."
    hdr_cells[1].text = "Diagram Title"
    hdr_cells[2].text = "Figure Number"
    for c in hdr_cells:
        set_cell_background(c, "E2E8F0")
        for p in c.paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(11)

    for d in DIAGRAMS_DATA:
        row_cells = table_toc.add_row().cells
        row_cells[0].text = str(d["num"])
        row_cells[1].text = d["title"]
        row_cells[2].text = d["figure_no"]
        for c in row_cells:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(11)

    doc.add_page_break()

    # Each Diagram Section
    for d in DIAGRAMS_DATA:
        diag_id = d["id"]

        # Heading
        p_head = doc.add_paragraph()
        p_head.paragraph_format.space_before = Pt(14)
        p_head.paragraph_format.space_after = Pt(6)
        r_head = p_head.add_run(f"{d['num']}. {d['title']}")
        r_head.bold = True
        r_head.font.size = Pt(15)
        r_head.font.color.rgb = RGBColor(26, 54, 93)

        # Description
        p_desc = doc.add_paragraph()
        p_desc.paragraph_format.space_after = Pt(10)
        r_desc = p_desc.add_run(d["desc"])
        r_desc.font.size = Pt(11.5)

        # Diagram Image
        png_path = rendered_map.get(diag_id)
        if png_path and os.path.exists(png_path):
            try:
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(8)
                p_img.paragraph_format.space_after = Pt(6)
                r_img = p_img.add_run()
                r_img.add_picture(png_path, width=Inches(5.6))
            except Exception as ex:
                print(f"Error adding picture for {diag_id}: {ex}")

        # Caption
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(d["caption"])
        r_cap.bold = True
        r_cap.font.italic = True
        r_cap.font.size = Pt(11)
        r_cap.font.color.rgb = RGBColor(45, 55, 72)

        # Components Table
        p_tbl_title = doc.add_paragraph()
        p_tbl_title.paragraph_format.space_before = Pt(6)
        p_tbl_title.paragraph_format.space_after = Pt(4)
        r_tbl_title = p_tbl_title.add_run("Key Components & Explanations:")
        r_tbl_title.bold = True
        r_tbl_title.font.size = Pt(11)

        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl)
        h_cells = tbl.rows[0].cells
        h_cells[0].text = "Component / Entity"
        h_cells[1].text = "Role & Description"
        for c in h_cells:
            set_cell_background(c, "F1F5F9")
            for p in c.paragraphs:
                for r in p.runs:
                    r.bold = True
                    r.font.size = Pt(10.5)

        for comp_name, comp_desc in d["components"]:
            r_c = tbl.add_row().cells
            r_c[0].text = comp_name
            r_c[1].text = comp_desc
            for c in r_c:
                for p in c.paragraphs:
                    for r in p.runs:
                        r.font.size = Pt(10)

        doc.add_page_break()

    # Save to Word file
    out_file_1 = os.path.join(BASE_DIR, "OPPORA_AI_Project_Report_Diagrams.docx")
    
    doc.save(out_file_1)
    print(f"\n[SUCCESS] Word document created: {out_file_1}")

if __name__ == "__main__":
    generate_all()
