from datetime import datetime, timedelta
import json
from app import create_app
from app.models import (
    db, User, StudentProfile, Skill, StudentSkill, StudentProject,
    StudentCertification, OpportunityCategory, Opportunity, Application
)

app = create_app()

def seed_database():
    with app.app_context():
        print("[*] Creating database tables if they do not exist...")
        db.create_all()

        print("[*] Seeding Master Skills...")
        skills_data = [
            ("Python", "programming_language"),
            ("JavaScript", "programming_language"),
            ("TypeScript", "programming_language"),
            ("Java", "programming_language"),
            ("C++", "programming_language"),
            ("Go", "programming_language"),
            ("SQL", "database"),
            ("PostgreSQL", "database"),
            ("MongoDB", "database"),
            ("Redis", "database"),
            ("React", "framework"),
            ("Node.js", "framework"),
            ("Flask", "framework"),
            ("FastAPI", "framework"),
            ("Django", "framework"),
            ("Next.js", "framework"),
            ("TailwindCSS", "framework"),
            ("Docker", "tool"),
            ("Kubernetes", "tool"),
            ("Git", "tool"),
            ("AWS", "cloud"),
            ("Google Cloud", "cloud"),
            ("Machine Learning", "data_ai"),
            ("Deep Learning", "data_ai"),
            ("PyTorch", "data_ai"),
            ("Data Structures & Algorithms", "general"),
            ("System Design", "general"),
            ("REST APIs", "general"),
            ("CI/CD", "tool"),
            ("Communication", "soft_skill")
        ]

        skill_objs = {}
        for name, category in skills_data:
            skill = Skill.query.filter_by(name=name).first()
            if not skill:
                skill = Skill(name=name, category=category)
                db.session.add(skill)
                db.session.flush()
            skill_objs[name] = skill

        print("[*] Seeding Opportunity Categories...")
        categories_data = [
            ("Software Engineering", "software-engineering", "code", "Full-stack, backend, frontend and system development opportunities."),
            ("Data Science & AI", "data-science-ai", "cpu", "Machine learning, data analytics, AI research and MLOps."),
            ("Cloud & DevOps", "cloud-devops", "cloud", "Infrastructure, cloud architecture, CI/CD, and site reliability."),
            ("Competitive Programming & Hackathons", "competitions-hackathons", "award", "Coding contests, collegiate competitions, and hackathons."),
            ("Professional Certifications", "certifications", "check-circle", "Accredited industry certifications from major cloud and tech providers.")
        ]

        cat_objs = {}
        for name, slug, icon, desc in categories_data:
            cat = OpportunityCategory.query.filter_by(slug=slug).first()
            if not cat:
                cat = OpportunityCategory(name=name, slug=slug, icon=icon, description=desc)
                db.session.add(cat)
                db.session.flush()
            cat_objs[slug] = cat

        print("[*] Seeding Opportunities (18+ sample opportunities across 6 types)...")
        now = datetime.utcnow()

        opportunities_data = [
            # 1. Internships
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "company_name": "Google",
                "opportunity_type": "internship",
                "category_slug": "software-engineering",
                "description": "Join Google's Core Engineering team to design, test, deploy, and maintain software solutions that impact billions of users worldwide. Work with large-scale distributed systems.",
                "location": "Mountain View, CA / Remote",
                "is_remote": True,
                "stipend_salary": "$9,500/month + Housing",
                "deadline": now + timedelta(days=45),
                "apply_url": "https://careers.google.com/students",
                "required_skills": ["Python", "C++", "Data Structures & Algorithms", "Git"],
                "eligibility_criteria": "Pursuing BS/MS in Computer Science or related STEM field. Graduation 2026-2027.",
                "experience_level": "Undergraduate"
            },
            {
                "title": "Cloud Infrastructure Intern",
                "company_name": "Microsoft Azure",
                "opportunity_type": "internship",
                "category_slug": "cloud-devops",
                "description": "Collaborate on next-generation Azure Cloud Services, focusing on container virtualization, Kubernetes orchestration, and telemetry dashboards.",
                "location": "Redmond, WA / Hybrid",
                "is_remote": True,
                "stipend_salary": "$8,800/month",
                "deadline": now + timedelta(days=30),
                "apply_url": "https://careers.microsoft.com/students",
                "required_skills": ["Docker", "Kubernetes", "Go", "Python", "AWS"],
                "eligibility_criteria": "Current student with strong background in operating systems and networking fundamentals.",
                "experience_level": "Undergraduate"
            },
            {
                "title": "Frontend Engineering Intern",
                "company_name": "Stripe",
                "opportunity_type": "internship",
                "category_slug": "software-engineering",
                "description": "Build beautiful, highly accessible developer dashboards and payment flows using React, TypeScript, and design systems.",
                "location": "San Francisco, CA / Remote",
                "is_remote": True,
                "stipend_salary": "$9,200/month",
                "deadline": now + timedelta(days=25),
                "apply_url": "https://stripe.com/jobs/students",
                "required_skills": ["React", "TypeScript", "JavaScript", "REST APIs", "TailwindCSS"],
                "eligibility_criteria": "Demonstrated experience building interactive web applications and UI components.",
                "experience_level": "Undergraduate"
            },
            {
                "title": "AI & Machine Learning Research Intern",
                "company_name": "NVIDIA",
                "opportunity_type": "internship",
                "category_slug": "data-science-ai",
                "description": "Develop and optimize deep learning algorithms and LLM inference pipelines leveraging CUDA, PyTorch, and TensorRT.",
                "location": "Santa Clara, CA / Remote",
                "is_remote": True,
                "stipend_salary": "$10,000/month",
                "deadline": now + timedelta(days=40),
                "apply_url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite",
                "required_skills": ["Python", "PyTorch", "Deep Learning", "Machine Learning", "C++"],
                "eligibility_criteria": "Strong mathematical foundation in linear algebra, probability, and neural networks.",
                "experience_level": "Undergraduate / Masters"
            },

            # 2. Hackathons
            {
                "title": "Global AI & Agentic Innovation Hackathon 2026",
                "company_name": "Google Cloud & Devpost",
                "opportunity_type": "hackathon",
                "category_slug": "competitions-hackathons",
                "description": "Build groundbreaking autonomous AI agents and multimodal applications utilizing Gemini 1.5/2.0 API. Over $100,000 in cash prizes and accelerator interviews.",
                "location": "Global Virtual Event",
                "is_remote": True,
                "stipend_salary": "Prize Pool: $100,000",
                "deadline": now + timedelta(days=20),
                "apply_url": "https://devpost.com/hackathons",
                "required_skills": ["Python", "JavaScript", "REST APIs", "Machine Learning", "FastAPI"],
                "eligibility_criteria": "Open to all students and developers worldwide. Teams of 1 to 4 members.",
                "experience_level": "All Levels"
            },
            {
                "title": "HackMIT 2026",
                "company_name": "MIT Tech Club",
                "opportunity_type": "hackathon",
                "category_slug": "competitions-hackathons",
                "description": "One of the world's most prestigious collegiate hackathons. 36 hours of hacking, mentorship from top tech leaders, and sponsor bounties.",
                "location": "Cambridge, MA / Hybrid",
                "is_remote": True,
                "stipend_salary": "Prizes: $50,000 + Hardware Grants",
                "deadline": now + timedelta(days=18),
                "apply_url": "https://hackmit.org",
                "required_skills": ["Python", "React", "Node.js", "Docker", "Git"],
                "eligibility_criteria": "Undergraduate and graduate students globally.",
                "experience_level": "All Levels"
            },
            {
                "title": "Open Source AI Buildathon",
                "company_name": "Hugging Face & GitHub",
                "opportunity_type": "hackathon",
                "category_slug": "data-science-ai",
                "description": "Create open-source AI tools, datasets, and fine-tuned models to advance accessibility in machine learning.",
                "location": "Virtual",
                "is_remote": True,
                "stipend_salary": "Prizes: $35,000 + Compute Credits",
                "deadline": now + timedelta(days=35),
                "apply_url": "https://huggingface.co/hackathons",
                "required_skills": ["Python", "PyTorch", "Git", "Docker"],
                "eligibility_criteria": "Open to developers building public GitHub repositories.",
                "experience_level": "All Levels"
            },

            # 3. Certifications
            {
                "title": "AWS Certified Solutions Architect - Associate",
                "company_name": "Amazon Web Services",
                "opportunity_type": "certification",
                "category_slug": "certifications",
                "description": "Showcase knowledge of AWS architecture, security, scalability, high availability, and cost-efficient cloud system designs.",
                "location": "Online Proctored",
                "is_remote": True,
                "stipend_salary": "Free Student Exam Vouchers Available",
                "deadline": now + timedelta(days=90),
                "apply_url": "https://aws.amazon.com/certification/certified-solutions-architect-associate/",
                "required_skills": ["AWS", "Docker", "System Design", "SQL"],
                "eligibility_criteria": "Students can apply for AWS Educate 50% discount vouchers.",
                "experience_level": "Intermediate"
            },
            {
                "title": "Meta Front-End Developer Professional Certificate",
                "company_name": "Meta / Coursera",
                "opportunity_type": "certification",
                "category_slug": "certifications",
                "description": "Comprehensive program covering React, JavaScript, CSS frameworks, UI/UX principles, version control, and capstone portfolio projects.",
                "location": "Self-Paced Online",
                "is_remote": True,
                "stipend_salary": "Financial Aid Available (100% Covered)",
                "deadline": now + timedelta(days=60),
                "apply_url": "https://www.coursera.org/professional-certificates/meta-front-end-developer",
                "required_skills": ["React", "JavaScript", "TailwindCSS", "Git"],
                "eligibility_criteria": "Beginner-friendly, no prior prerequisites required.",
                "experience_level": "Beginner / Intermediate"
            },
            {
                "title": "Google Cloud Professional Data Engineer",
                "company_name": "Google Cloud",
                "opportunity_type": "certification",
                "category_slug": "certifications",
                "description": "Validate your ability to design, build, operationalize, and secure data processing systems on GCP (BigQuery, Dataflow, Vertex AI).",
                "location": "Online Exam",
                "is_remote": True,
                "stipend_salary": "Industry Credential",
                "deadline": now + timedelta(days=75),
                "apply_url": "https://cloud.google.com/certification/data-engineer",
                "required_skills": ["SQL", "Google Cloud", "Python", "Data Structures & Algorithms"],
                "eligibility_criteria": "Recommended for students with foundational database and Python skills.",
                "experience_level": "Intermediate / Advanced"
            },

            # 4. Courses
            {
                "title": "CS50x: Introduction to Computer Science",
                "company_name": "Harvard University",
                "opportunity_type": "course",
                "category_slug": "software-engineering",
                "description": "An introduction to the intellectual enterprises of computer science and the art of programming (C, Python, SQL, HTML/CSS, Flask).",
                "location": "Self-Paced Online",
                "is_remote": True,
                "stipend_salary": "Free (Certificate Included)",
                "deadline": now + timedelta(days=120),
                "apply_url": "https://pll.harvard.edu/course/cs50-introduction-computer-science",
                "required_skills": ["Python", "SQL", "C++", "Flask"],
                "eligibility_criteria": "Open to everyone with curious minds.",
                "experience_level": "Beginner"
            },
            {
                "title": "Full Stack Open: Deep Dive into Modern Web Development",
                "company_name": "University of Helsinki",
                "opportunity_type": "course",
                "category_slug": "software-engineering",
                "description": "Learn React, Redux, Node.js, MongoDB, GraphQL, TypeScript, and Docker containerization with comprehensive exercises.",
                "location": "Online Self-Paced",
                "is_remote": True,
                "stipend_salary": "100% Free / University Credits",
                "deadline": now + timedelta(days=90),
                "apply_url": "https://fullstackopen.com",
                "required_skills": ["JavaScript", "TypeScript", "React", "Node.js", "MongoDB", "Docker"],
                "eligibility_criteria": "Basic familiarity with programming.",
                "experience_level": "Intermediate"
            },
            {
                "title": "Machine Learning Specialization",
                "company_name": "DeepLearning.AI & Stanford",
                "opportunity_type": "course",
                "category_slug": "data-science-ai",
                "description": "Master foundational machine learning concepts, supervised learning, neural networks, decision trees, and reinforcement learning by Andrew Ng.",
                "location": "Online",
                "is_remote": True,
                "stipend_salary": "Audit Free",
                "deadline": now + timedelta(days=80),
                "apply_url": "https://www.coursera.org/specializations/machine-learning-introduction",
                "required_skills": ["Python", "Machine Learning", "Data Structures & Algorithms"],
                "eligibility_criteria": "Basic high school math and Python syntax.",
                "experience_level": "Beginner / Intermediate"
            },

            # 5. Competitions
            {
                "title": "Kaggle LLM Prompt Engineering & Reasoning Challenge",
                "company_name": "Kaggle",
                "opportunity_type": "competition",
                "category_slug": "data-science-ai",
                "description": "Benchmark complex reasoning models on multi-step question answering datasets. Compete with top data scientists globally.",
                "location": "Online",
                "is_remote": True,
                "stipend_salary": "Prizes: $75,000",
                "deadline": now + timedelta(days=28),
                "apply_url": "https://www.kaggle.com/competitions",
                "required_skills": ["Python", "PyTorch", "Machine Learning", "Deep Learning"],
                "eligibility_criteria": "Free Kaggle account registration.",
                "experience_level": "All Levels"
            },
            {
                "title": "International Collegiate Programming Contest (ICPC) Qualifiers",
                "company_name": "ICPC Global Foundation",
                "opportunity_type": "competition",
                "category_slug": "competitions-hackathons",
                "description": "The premier global algorithmic programming contest for college students. Solve complex algorithmic challenges under strict time and memory limits.",
                "location": "Regional Sites & Online",
                "is_remote": True,
                "stipend_salary": "Global Recognition & Trophies",
                "deadline": now + timedelta(days=22),
                "apply_url": "https://icpc.global",
                "required_skills": ["C++", "Java", "Python", "Data Structures & Algorithms"],
                "eligibility_criteria": "Enrolled university undergraduate students.",
                "experience_level": "Advanced"
            },

            # 6. Jobs (Entry-Level / Graduate)
            {
                "title": "Associate Software Development Engineer (New Grad 2026)",
                "company_name": "Atlassian",
                "opportunity_type": "job",
                "category_slug": "software-engineering",
                "description": "Build high-impact collaboration software (Jira, Confluence) used by millions. Modern microservices, React, TypeScript, and AWS cloud native backends.",
                "location": "Bengaluru / Austin / Remote",
                "is_remote": True,
                "stipend_salary": "$115,000 - $130,000 / year + Equity",
                "deadline": now + timedelta(days=50),
                "apply_url": "https://www.atlassian.com/company/careers/graduates",
                "required_skills": ["Java", "TypeScript", "React", "SQL", "AWS", "REST APIs"],
                "eligibility_criteria": "Graduating in 2025 or 2026 with a degree in Computer Science, Software Engineering or related discipline.",
                "experience_level": "Entry Level (0-1 yrs)"
            },
            {
                "title": "Junior Full-Stack Engineer",
                "company_name": "Vercel",
                "opportunity_type": "job",
                "category_slug": "software-engineering",
                "description": "Empower millions of frontend developers by building edge deployment pipelines, web analytics dashboards, and Next.js developer experience features.",
                "location": "Global Remote",
                "is_remote": True,
                "stipend_salary": "$110,000 - $135,000 / year",
                "deadline": now + timedelta(days=35),
                "apply_url": "https://vercel.com/careers",
                "required_skills": ["Next.js", "TypeScript", "React", "Node.js", "Docker", "Git"],
                "eligibility_criteria": "Strong portfolio of production Next.js / TypeScript projects.",
                "experience_level": "Entry Level"
            },
            {
                "title": "Junior DevOps & Site Reliability Engineer",
                "company_name": "Datadog",
                "opportunity_type": "job",
                "category_slug": "cloud-devops",
                "description": "Help scale our multi-cloud telemetry infrastructure ingesting trillions of events daily. Manage Kubernetes clusters, Terraform IaC, and automated monitoring pipelines.",
                "location": "Boston, MA / Remote",
                "is_remote": True,
                "stipend_salary": "$118,000 / year",
                "deadline": now + timedelta(days=42),
                "apply_url": "https://www.datadoghq.com/careers",
                "required_skills": ["Docker", "Kubernetes", "Python", "Go", "AWS", "CI/CD"],
                "eligibility_criteria": "Bachelor's in Computer Science or equivalent hands-on Linux/Cloud experience.",
                "experience_level": "Entry Level"
            }
        ]

        for item in opportunities_data:
            existing = Opportunity.query.filter_by(title=item['title'], company_name=item['company_name']).first()
            category = cat_objs.get(item.get('category_slug'))
            if not existing:
                opp = Opportunity(
                    title=item['title'],
                    company_name=item['company_name'],
                    opportunity_type=item['opportunity_type'],
                    category_id=category.id if category else None,
                    description=item['description'],
                    location=item['location'],
                    is_remote=item['is_remote'],
                    stipend_salary=item['stipend_salary'],
                    deadline=item['deadline'],
                    apply_url=item['apply_url'],
                    required_skills=item['required_skills'],
                    eligibility_criteria=item['eligibility_criteria'],
                    status='active',
                    experience_level=item['experience_level']
                )
                db.session.add(opp)

        db.session.flush()

        print("[*] Seeding Demo Users (Admin & Student)...")

        # 1. Admin User
        admin_user = User.query.filter_by(email="admin@careerdna.ai").first()
        if not admin_user:
            admin_user = User(email="admin@careerdna.ai", role="admin")
            admin_user.set_password("Admin@123")
            db.session.add(admin_user)
            print("  Created Admin: admin@careerdna.ai / Admin@123")

        # 2. Student User with Full Profile
        student_user = User.query.filter_by(email="student@careerdna.ai").first()
        if not student_user:
            student_user = User(email="student@careerdna.ai", role="student")
            student_user.set_password("Student@123")
            db.session.add(student_user)
            db.session.flush()
            print("  Created Student: student@careerdna.ai / Student@123")

            profile = StudentProfile(
                user_id=student_user.id,
                full_name="Alex Morgan",
                headline="Computer Science Senior | Full-Stack & AI Enthusiast",
                phone="+1 (555) 234-5678",
                college_name="Stanford University",
                degree="Bachelor of Science",
                branch="Computer Science",
                graduation_year=2026,
                cgpa=8.8,
                bio="Passionate full-stack software engineer and machine learning enthusiast with experience building web applications, REST APIs, and data pipelines. Looking for high-growth software engineering internships and graduate roles.",
                career_goal="Full-Stack Software Engineer & Distributed Systems Developer",
                target_role="Full-Stack Software Engineer",
                interests="Cloud Computing, AI Agents, Web Performance, Open Source, Distributed Systems",
                github_url="https://github.com/alexmorgan-dev",
                linkedin_url="https://linkedin.com/in/alexmorgan-dev",
                portfolio_url="https://alexmorgan.dev"
            )
            db.session.add(profile)
            db.session.flush()

            # Student skills
            student_skills = [
                ("Python", "advanced", 3.0),
                ("JavaScript", "advanced", 3.0),
                ("TypeScript", "intermediate", 2.0),
                ("React", "advanced", 2.5),
                ("Node.js", "intermediate", 2.0),
                ("SQL", "advanced", 2.5),
                ("Docker", "intermediate", 1.5),
                ("Git", "advanced", 3.0),
                ("REST APIs", "advanced", 2.5)
            ]
            for s_name, prof, yoe in student_skills:
                m_skill = skill_objs.get(s_name)
                s_skill = StudentSkill(
                    student_id=profile.id,
                    skill_id=m_skill.id if m_skill else None,
                    skill_name=s_name,
                    proficiency_level=prof,
                    years_of_experience=yoe
                )
                db.session.add(s_skill)

            # Student projects
            p1 = StudentProject(
                student_id=profile.id,
                title="Career DNA AI — Opportunity & Career Intelligence Platform",
                description="Engineered an AI-powered student recommendation platform with personalized skill gap analytics, dynamic roadmap generation, and ReportLab PDF resume exports.",
                tech_stack="Python, Flask, JavaScript, MySQL, Gemini API, ReportLab",
                github_url="https://github.com/alexmorgan-dev/career-dna-ai",
                live_url="https://careerdna.ai",
                role="Lead Full-Stack Developer"
            )
            p2 = StudentProject(
                student_id=profile.id,
                title="Distributed Task Queue & Real-Time Event Streamer",
                description="Built a high-throughput async task processing worker in Python and Redis handling 2,000+ jobs/second with automatic retry exponential backoff.",
                tech_stack="Python, FastAPI, Redis, Docker, PostgreSQL",
                github_url="https://github.com/alexmorgan-dev/task-streamer",
                live_url="https://tasks.alexmorgan.dev",
                role="Backend Architect"
            )
            db.session.add_all([p1, p2])

            # Student Certifications
            c1 = StudentCertification(
                student_id=profile.id,
                title="AWS Certified Solutions Architect - Associate",
                issuing_organization="Amazon Web Services",
                issue_date="2025-03",
                credential_id="AWS-SAA-839210",
                credential_url="https://aws.amazon.com/verify"
            )
            c2 = StudentCertification(
                student_id=profile.id,
                title="Meta Front-End Developer Certificate",
                issuing_organization="Meta",
                issue_date="2024-11",
                credential_id="META-FE-992144",
                credential_url="https://coursera.org/verify/meta"
            )
            db.session.add_all([c1, c2])

            # Sample Applications
            app1 = Application(
                student_id=profile.id,
                company_name="Google",
                position_title="Software Engineering Intern",
                opportunity_type="internship",
                status="interview_scheduled",
                applied_date=(now - timedelta(days=12)).date(),
                interview_date=now + timedelta(days=5, hours=14),
                deadline=(now + timedelta(days=45)).date(),
                notes="Technical coding round scheduled covering Trees & Graph traversal. Review LeetCode 75.",
                salary_offered="$9,500/month"
            )
            app2 = Application(
                student_id=profile.id,
                company_name="Stripe",
                position_title="Frontend Engineering Intern",
                opportunity_type="internship",
                status="in_progress",
                applied_date=(now - timedelta(days=8)).date(),
                notes="Completed initial screening questionnaire. Waiting for recruiter review."
            )
            app3 = Application(
                student_id=profile.id,
                company_name="Vercel",
                position_title="Junior Full-Stack Engineer",
                opportunity_type="job",
                status="applied",
                applied_date=(now - timedelta(days=3)).date(),
                notes="Submitted portfolio project links."
            )
            db.session.add_all([app1, app2, app3])

            profile.calculate_completion_pct()

        db.session.commit()
        print("[SUCCESS] Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
