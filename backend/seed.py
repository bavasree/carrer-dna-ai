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
            ("Azure", "cloud"),
            ("Machine Learning", "data_ai"),
            ("Deep Learning", "data_ai"),
            ("PyTorch", "data_ai"),
            ("Data Structures & Algorithms", "general"),
            ("System Design", "general"),
            ("REST APIs", "general"),
            ("CI/CD", "tool"),
            ("Solidity", "blockchain"),
            ("Linux", "tool"),
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
            ("Competitions & Hackathons", "competitions-hackathons", "award", "Coding contests, collegiate competitions, and hackathons."),
            ("Professional Certifications", "certifications", "check-circle", "Accredited industry certifications from major cloud and tech providers."),
            ("Workshops & Tech Bootcamps", "workshops", "mortarboard", "Interactive masterclasses, hands-on architectural bootcamps and webinars.")
        ]

        cat_objs = {}
        for name, slug, icon, desc in categories_data:
            cat = OpportunityCategory.query.filter_by(slug=slug).first()
            if not cat:
                cat = OpportunityCategory(name=name, slug=slug, icon=icon, description=desc)
                db.session.add(cat)
                db.session.flush()
            cat_objs[slug] = cat

        print("[*] Seeding Comprehensive Real-World Opportunities (33+ opportunities)...")
        now = datetime.utcnow()

        opportunities_data = [
            # =========================================================================
            # 1. HACKATHONS
            # =========================================================================
            {
                "title": "Smart India Hackathon (SIH 2026)",
                "company_name": "Ministry of Education & AICTE",
                "opportunity_type": "hackathon",
                "category_slug": "competitions-hackathons",
                "organizer_type": "Government / AICTE",
                "description": "World's largest open-innovation digital hackathon addressing real-world problem statements posed by central ministries, state governments, and premier industries.",
                "location": "New Delhi / 40+ Nodal Centers Across India",
                "venue_address": "Nationwide Premier Institutional Nodal Centers & AICTE HQ, Nelson Mandela Marg, New Delhi",
                "is_remote": False,
                "event_mode": "Offline (In-Person Grand Finale)",
                "event_date": "October 22 - 24, 2026 (36 Hours Non-stop)",
                "registration_fee": "Free to Participate",
                "team_size": "6 Members (Mandatory min. 1 female hacker)",
                "stipend_salary": "₹1,00,000 per Problem Statement (₹1.5+ Cr Pool)",
                "prize_details": "₹1,00,000 Cash Prize for each winning team per problem statement, incubation support, AICTE certificates, direct access to Govt internships.",
                "duration": "36-Hour Continuous Hackathon",
                "perks": ["Govt of India Official Certificate", "Incubation & Seed Funding Grant", "Direct Ministry Internship Interviews", "Free Travel & Stay provided at Nodal Centers"],
                "schedule": [
                    {"phase": "Internal College Nominations", "date": "Sep 20, 2026"},
                    {"phase": "National Idea Submission Deadline", "date": "Oct 05, 2026"},
                    {"phase": "Shortlisting Announcement", "date": "Oct 12, 2026"},
                    {"phase": "Grand Finale Hackathon", "date": "Oct 22 - 24, 2026"}
                ],
                "deadline": now + timedelta(days=6),
                "apply_url": "https://sih.gov.in",
                "contact_email": "hackathon@aicte-india.org",
                "required_skills": ["Python", "React", "Node.js", "Machine Learning", "FastAPI", "SQL"],
                "eligibility_criteria": "Regular full-time undergraduate & postgraduate engineering students in batches 2025-2028. College SPOC endorsement required.",
                "experience_level": "All Levels"
            },
            {
                "title": "EthIndia 2026 — Asia's Biggest Web3 Hackathon",
                "company_name": "Devfolio & Ethereum Foundation",
                "opportunity_type": "hackathon",
                "category_slug": "competitions-hackathons",
                "organizer_type": "Global Community",
                "description": "Join 2,000+ top builders, protocol architects, and designers at Asia's premier Ethereum hackathon. Build decentralized apps, ZK systems, and smart contracts.",
                "location": "KTPO Convention Center, Whitefield, Bangalore",
                "venue_address": "KTPO Trade Center, Plot No 121, Export Promotion Industrial Park, Whitefield, Bengaluru, Karnataka 560066",
                "is_remote": False,
                "event_mode": "Offline (In-Person)",
                "event_date": "December 04 - 06, 2026",
                "registration_fee": "Free (Application Review Basis)",
                "team_size": "2 to 4 Members",
                "stipend_salary": "$60,000+ in Track Bounties & Grants",
                "prize_details": "$60,000+ (₹50 Lakhs) across main prizes and sponsor bounties (Polygon, Arbitrum, Base, Uniswap, Chainlink) + VC accelerator pitching.",
                "duration": "36-Hour In-Person Sprint",
                "perks": ["Flight/Travel Scholarship Reimbursed", "Official EthIndia Swag & Hardware Wallet", "Direct VC & Angel Seed Pitching", "Exclusive Hacker Feast & Red Bull Lounge"],
                "schedule": [
                    {"phase": "Hacker Application Opens", "date": "Sep 01, 2026"},
                    {"phase": "Early Wave Review", "date": "Oct 15, 2026"},
                    {"phase": "Final Registration Closes", "date": "Nov 10, 2026"},
                    {"phase": "Hacking Kickoff & Demos", "date": "Dec 04 - 06, 2026"}
                ],
                "deadline": now + timedelta(days=22),
                "apply_url": "https://ethindia.co",
                "contact_email": "hello@devfolio.co",
                "required_skills": ["Solidity", "TypeScript", "React", "Next.js", "Docker", "Git"],
                "eligibility_criteria": "Open to all developers, designers, and students globally. Selection based on GitHub and prior project track record.",
                "experience_level": "Intermediate / Advanced"
            },
            {
                "title": "Google Cloud & Devpost GenAI Agentic Hackathon",
                "company_name": "Google Cloud & Devpost",
                "opportunity_type": "hackathon",
                "category_slug": "data-science-ai",
                "organizer_type": "Tech Company",
                "description": "Design and build autonomous agentic workflows, multi-agent collaborations, and enterprise AI tools using Gemini 2.0 Flash, Vertex AI, and Function Calling.",
                "location": "Global Virtual / Devpost Platform",
                "venue_address": "Online Discord & Devpost Submissions Hub",
                "is_remote": True,
                "event_mode": "Online (Virtual)",
                "event_date": "November 10 - 25, 2026",
                "registration_fee": "Free",
                "team_size": "1 to 4 Members",
                "stipend_salary": "Prize Pool: $100,000 (₹83 Lakhs)",
                "prize_details": "1st: $35,000 • 2nd: $20,000 • 3rd: $10,000 • Best Multimodal Agent: $7,500 • $1,000 GCP credits for all top 50 submissions.",
                "duration": "2-Week Online Hackathon",
                "perks": ["$500 Free Vertex AI API Credits", "Google Cloud Digital Certificate", "Mentorship from Google Staff ML Engineers", "Fast-track interview for Google Cloud AI Fellows"],
                "schedule": [
                    {"phase": "Registrations Open", "date": "Oct 01, 2026"},
                    {"phase": "API Keys Dispatched", "date": "Nov 10, 2026"},
                    {"phase": "Submission Deadline", "date": "Nov 25, 2026"},
                    {"phase": "Live Demo & Winner Showcase", "date": "Dec 05, 2026"}
                ],
                "deadline": now + timedelta(days=15),
                "apply_url": "https://devpost.com/hackathons",
                "contact_email": "googlecloud-hack@devpost.com",
                "required_skills": ["Python", "FastAPI", "Machine Learning", "Deep Learning", "REST APIs", "Git"],
                "eligibility_criteria": "Open to all university students and independent software developers worldwide (18+).",
                "experience_level": "All Levels"
            },
            {
                "title": "Flipkart GRiD 6.0 — Engineering Campus Challenge",
                "company_name": "Flipkart",
                "opportunity_type": "hackathon",
                "category_slug": "software-engineering",
                "organizer_type": "Tech Company",
                "description": "Flipkart's flagship collegiate hackathon across Software Development, Information Security, and Robotics. Real enterprise e-commerce scale problems.",
                "location": "Online Rounds + Flipkart HQ, Bangalore Finale",
                "venue_address": "Flipkart Internet Pvt Ltd, Buildings Alyssa, Begonia & Clover, Embassy Tech Village, Outer Ring Road, Devarabeesanahalli, Bengaluru, Karnataka 560103",
                "is_remote": False,
                "event_mode": "Hybrid (Online Rounds + In-Person Finale)",
                "event_date": "October 28 - 30, 2026",
                "registration_fee": "Free",
                "team_size": "2 to 3 Members",
                "stipend_salary": "₹5,25,000 Cash + SDE-1 Job Offers (₹32 LPA)",
                "prize_details": "National Winner: ₹3,00,000 • 1st Runner Up: ₹1,50,000 • PPI/PPO SDE-1 Interviews (CTC ₹32 LPA) for all national finalists.",
                "duration": "Multi-stage (Online Quiz, Proof-of-Concept, Grand Finale)",
                "perks": ["Direct SDE-1 Pre-Placement Interview (PPI)", "All-expenses paid trip to Flipkart HQ Bangalore", "Flipkart Vouchers & Merchandise Kit", "Executive Mentorship"],
                "schedule": [
                    {"phase": "Round 1: E-Commerce Tech Quiz", "date": "Oct 10, 2026"},
                    {"phase": "Round 2: Prototype Video Submission", "date": "Oct 20, 2026"},
                    {"phase": "National Grand Finale Hack", "date": "Oct 28 - 30, 2026"}
                ],
                "deadline": now + timedelta(days=4),
                "apply_url": "https://unstop.com/hackathons/flipkart-grid",
                "contact_email": "grid@flipkart.com",
                "required_skills": ["Data Structures & Algorithms", "System Design", "Java", "Python", "SQL", "Docker"],
                "eligibility_criteria": "B.Tech/B.E./M.Tech students graduating in batch 2026, 2027, or 2028 across all recognized Indian engineering colleges.",
                "experience_level": "Intermediate / Advanced"
            },
            {
                "title": "HackMIT 2026",
                "company_name": "MIT Tech Club",
                "opportunity_type": "hackathon",
                "category_slug": "competitions-hackathons",
                "organizer_type": "College / University",
                "description": "MIT's premier undergraduate hackathon bringing together 1,000+ collegiate hackers from across the world to build high-impact technologies.",
                "location": "Cambridge, MA, USA & Global Virtual",
                "venue_address": "Johnson Athletics Center, Massachusetts Institute of Technology, 120 Vassar St, Cambridge, MA 02139",
                "is_remote": True,
                "event_mode": "Hybrid (On-Campus & Virtual Discord)",
                "event_date": "November 14 - 16, 2026",
                "registration_fee": "Free",
                "team_size": "1 to 4 Members",
                "stipend_salary": "Prizes: $50,000 + Hardware Kits",
                "prize_details": "Grand Prize: $15,000 • Category tracks (HealthTech, FinTech, Education, Sustainability): $5,000 each + Hardware lab grants & Oculus kits.",
                "duration": "36-Hour Hackathon",
                "perks": ["Exclusive MIT Hackathon Certificate", "Hardware Lab Access (Raspberry Pi, VR)", "Sponsor Recruiting Booths (Jane Street, OpenAI, Figma)", "Swag Pack delivered worldwide"],
                "schedule": [
                    {"phase": "Registration Deadline", "date": "Oct 28, 2026"},
                    {"phase": "Team Formation & Teardowns", "date": "Nov 12, 2026"},
                    {"phase": "36-Hour Hacking Period", "date": "Nov 14 - 16, 2026"}
                ],
                "deadline": now + timedelta(days=12),
                "apply_url": "https://hackmit.org",
                "contact_email": "help@hackmit.org",
                "required_skills": ["Python", "React", "Node.js", "Docker", "Git", "REST APIs"],
                "eligibility_criteria": "Undergraduate and graduate university students worldwide.",
                "experience_level": "All Levels"
            },

            # =========================================================================
            # 2. INTERNSHIPS
            # =========================================================================
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "company_name": "Google",
                "opportunity_type": "internship",
                "category_slug": "software-engineering",
                "organizer_type": "Tech Company",
                "description": "Work side-by-side with Google software engineers on mission-critical applications across Search, Maps, Cloud, Android, and YouTube. Design scalable backend services and distributed algorithms.",
                "location": "Bengaluru / Hyderabad, India (Hybrid)",
                "venue_address": "Google Signature Towers, Outer Ring Road, Bellandur, Bengaluru, Karnataka 560103",
                "is_remote": False,
                "event_mode": "Hybrid",
                "event_date": "May 18 - July 24, 2026 (10 Weeks)",
                "registration_fee": "Free (Direct Application)",
                "team_size": "Individual",
                "stipend_salary": "₹1,25,000/month + Free Housing & Food",
                "prize_details": "Pre-Placement Offer (PPO) potential for full-time Software Engineer (L3) with package of ₹35+ LPA.",
                "duration": "10 to 12 Weeks (Summer Internship)",
                "perks": ["Pre-Placement Offer (PPO) Conversion", "Free Gourmet Breakfast, Lunch & Dinner", "Comprehensive Health Insurance", "1-on-1 Mentorship from Google Staff Engineers", "MacBook Pro M3 Max provided"],
                "schedule": [
                    {"phase": "Application Screening", "date": "Oct 15, 2026"},
                    {"phase": "Online Coding Assessment (2 Qs, 90 mins)", "date": "Oct 25, 2026"},
                    {"phase": "Technical Interviews (2 Rounds DSA)", "date": "Nov 10, 2026"},
                    {"phase": "Internship Commences", "date": "May 18, 2026"}
                ],
                "deadline": now + timedelta(days=20),
                "apply_url": "https://careers.google.com/students",
                "contact_email": "campus-recruiting@google.com",
                "required_skills": ["Data Structures & Algorithms", "C++", "Python", "Java", "Git", "System Design"],
                "eligibility_criteria": "Pursuing B.Tech/B.E./Dual Degree in Computer Science, IT, ECE with graduation year 2026 or 2027. Min. 7.5 CGPA.",
                "experience_level": "Undergraduate (3rd / 4th Year)"
            },
            {
                "title": "Cloud Infrastructure & SRE Intern",
                "company_name": "Microsoft Azure",
                "opportunity_type": "internship",
                "category_slug": "cloud-devops",
                "organizer_type": "Tech Company",
                "description": "Collaborate on next-generation Azure Cloud Services, focusing on container virtualization, Kubernetes orchestration, telemetry dashboards, and fault-tolerant distributed infrastructure.",
                "location": "Hyderabad / Bengaluru, India (Hybrid)",
                "venue_address": "Microsoft India Development Center (IDC), Gachibowli, Hyderabad, Telangana 500032",
                "is_remote": False,
                "event_mode": "Hybrid",
                "event_date": "Jan 12 - June 26, 2026 (6 Months)",
                "registration_fee": "Free",
                "team_size": "Individual",
                "stipend_salary": "₹1,00,000/month + Relocation Allowance",
                "prize_details": "Direct Fast-track PPO evaluation for Microsoft Azure Cloud SDE-1.",
                "duration": "6 Months (Spring Semester Internship)",
                "perks": ["Direct PPO Conversion Opportunity", "₹50,000 One-time Relocation Allowance", "Wellness & Gym Subsidy", "Surface Pro & Cloud Sandbox Access"],
                "schedule": [
                    {"phase": "Resume Shortlist", "date": "Oct 18, 2026"},
                    {"phase": "Codility Technical Test", "date": "Oct 28, 2026"},
                    {"phase": "Virtual Interview Loop (System + DSA)", "date": "Nov 15, 2026"}
                ],
                "deadline": now + timedelta(days=14),
                "apply_url": "https://careers.microsoft.com/students",
                "contact_email": "university_india@microsoft.com",
                "required_skills": ["Docker", "Kubernetes", "Go", "Python", "AWS", "Linux", "CI/CD"],
                "eligibility_criteria": "Current student with strong background in operating systems, networking fundamentals, and Linux.",
                "experience_level": "Undergraduate / Postgraduate"
            },
            {
                "title": "Amazon Software Development Engineer Intern (Summer 2026)",
                "company_name": "Amazon",
                "opportunity_type": "internship",
                "category_slug": "software-engineering",
                "organizer_type": "Tech Company",
                "description": "Design and build scalable microservices, automated order processing pipelines, and high-performance AWS cloud backend applications serving millions of customers.",
                "location": "Bengaluru / Chennai / Hyderabad, India",
                "venue_address": "Amazon Development Center, Bagmane Constellation Business Park, Doddanekkundi, Bengaluru, Karnataka 560037",
                "is_remote": False,
                "event_mode": "Hybrid",
                "event_date": "May 2026 - July 2026",
                "registration_fee": "Free",
                "team_size": "Individual",
                "stipend_salary": "₹1,10,000/month + ₹25,000 HRA/month",
                "prize_details": "High PPO conversion rate (>80%) for SDE-1 roles at ₹44 LPA CTC.",
                "duration": "2 to 6 Months",
                "perks": ["High Conversion Rate to Full-Time SDE-1", "Monthly Housing Allowance (₹25k)", "Amazon Prime & Device Discounts", "Cab Transportation Provided"],
                "schedule": [
                    {"phase": "Application Closes", "date": "Oct 20, 2026"},
                    {"phase": "Amazon Online Assessment (OA1 + OA2)", "date": "Nov 02, 2026"},
                    {"phase": "Technical Interviews", "date": "Nov 20, 2026"}
                ],
                "deadline": now + timedelta(days=16),
                "apply_url": "https://amazon.jobs/en/teams/internships-for-students",
                "contact_email": "student-jobs@amazon.com",
                "required_skills": ["Java", "C++", "Data Structures & Algorithms", "SQL", "REST APIs", "Git"],
                "eligibility_criteria": "Graduation in 2026 or 2027 with CS, IT, Software Engineering or related branches. Min. 7.0 CGPA.",
                "experience_level": "Undergraduate"
            },
            {
                "title": "AI & Deep Learning Research Intern",
                "company_name": "NVIDIA",
                "opportunity_type": "internship",
                "category_slug": "data-science-ai",
                "organizer_type": "Tech Company",
                "description": "Develop and benchmark large language model inference accelerators, TensorRT kernels, and computer vision models utilizing CUDA and PyTorch.",
                "location": "Pune, India / Santa Clara, CA (Remote Friendly)",
                "venue_address": "NVIDIA Graphics Pvt Ltd, Commerzone IT Park, Yerawada, Pune, Maharashtra 411006",
                "is_remote": True,
                "event_mode": "Remote / Hybrid",
                "event_date": "Jan 2026 - June 2026",
                "registration_fee": "Free",
                "team_size": "Individual",
                "stipend_salary": "₹1,20,000/month ($10,000/mo for US)",
                "prize_details": "Opportunity to publish research papers at NeurIPS / CVPR and direct AI Research Scientist full-time conversion.",
                "duration": "6 Months",
                "perks": ["Remote Work Flexibility & Equipment Allowance", "Access to NVIDIA DGX H100 GPU Clusters", "Co-authorship on Top-Tier AI Conference Papers", "Comprehensive Health Benefits"],
                "schedule": [
                    {"phase": "Application Deadline", "date": "Oct 30, 2026"},
                    {"phase": "AI/Math Technical Challenge", "date": "Nov 12, 2026"},
                    {"phase": "Research Panel Interview", "date": "Dec 01, 2026"}
                ],
                "deadline": now + timedelta(days=26),
                "apply_url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite",
                "contact_email": "universityrecruiting@nvidia.com",
                "required_skills": ["Python", "PyTorch", "Deep Learning", "Machine Learning", "C++", "Linux"],
                "eligibility_criteria": "Strong mathematical foundation in linear algebra, multivariable calculus, and neural network architectures. Pre-final / final year BS, MS, or PhD.",
                "experience_level": "Undergraduate / Masters / PhD"
            },
            {
                "title": "Frontend Engineering Intern (UI/UX Systems)",
                "company_name": "Stripe",
                "opportunity_type": "internship",
                "category_slug": "software-engineering",
                "organizer_type": "Tech Company",
                "description": "Build high-performance, accessible developer dashboards, payment flows, and micro-animations using React, TypeScript, and modern component systems.",
                "location": "Bengaluru, India / Global Remote",
                "venue_address": "Stripe India, Cowrks, RMZ Infinity, Old Madras Rd, Bengaluru, Karnataka 560016",
                "is_remote": True,
                "event_mode": "Remote",
                "event_date": "May 2026 - August 2026",
                "registration_fee": "Free",
                "team_size": "Individual",
                "stipend_salary": "₹95,000/month + $1,500 WFH Setup Kit",
                "prize_details": "PPO conversion for New Grad Frontend Engineer at ₹30+ LPA.",
                "duration": "12 Weeks",
                "perks": ["100% Remote Flexibility", "Home Office Setup Budget ($1,500)", "Direct Mentorship from Staff UI Engineers", "Flexible Working Hours"],
                "schedule": [
                    {"phase": "Applications Review", "date": "Oct 16, 2026"},
                    {"phase": "Frontend Coding Assignment (React Component)", "date": "Oct 26, 2026"},
                    {"phase": "Pair Programming Interview", "date": "Nov 08, 2026"}
                ],
                "deadline": now + timedelta(days=11),
                "apply_url": "https://stripe.com/jobs/students",
                "contact_email": "recruiting@stripe.com",
                "required_skills": ["React", "TypeScript", "JavaScript", "TailwindCSS", "REST APIs", "Git"],
                "eligibility_criteria": "Demonstrated expertise building responsive web apps with high UI polish and clean code architecture.",
                "experience_level": "Undergraduate (2026/2027 batch)"
            },
            {
                "title": "Backend Platform Engineering Intern",
                "company_name": "CRED",
                "opportunity_type": "internship",
                "category_slug": "software-engineering",
                "organizer_type": "Tech Company",
                "description": "Architect ultra-low latency fintech microservices, high-throughput Redis caching layers, and payment settlement pipelines processing billions of INR in transactions.",
                "location": "Indiranagar, Bangalore (On-site)",
                "venue_address": "CRED, 12th Main Rd, HAL 2nd Stage, Indiranagar, Bengaluru, Karnataka 560038",
                "is_remote": False,
                "event_mode": "Offline (On-Site)",
                "event_date": "Jan 2026 - June 2026",
                "registration_fee": "Free",
                "team_size": "Individual",
                "stipend_salary": "₹80,000/month + Free Gourmet Food",
                "prize_details": "Fast-track full-time SDE-1 offer (₹28 LPA + ESOPs).",
                "duration": "6 Months",
                "perks": ["Pre-Placement Offer (PPO) Conversion", "Free In-house Chef Gourmet Meals & Espresso Bar", "MacBook Pro M3 Max provided", "Cab Reimbursements"],
                "schedule": [
                    {"phase": "Hackathon / Assignment Round", "date": "Oct 22, 2026"},
                    {"phase": "System Architecture Discussion", "date": "Nov 05, 2026"}
                ],
                "deadline": now + timedelta(days=8),
                "apply_url": "https://careers.cred.club",
                "contact_email": "talent@cred.club",
                "required_skills": ["Node.js", "Go", "PostgreSQL", "Redis", "Docker", "System Design"],
                "eligibility_criteria": "Final year engineering students graduating in 2026 with strong backend fundamentals.",
                "experience_level": "Undergraduate"
            },
            {
                "title": "Space Science & Image Processing Intern",
                "company_name": "ISRO (Indian Space Research Organisation)",
                "opportunity_type": "internship",
                "category_slug": "data-science-ai",
                "organizer_type": "Government / Research",
                "description": "Contribute to satellite image analysis, geospatial computer vision algorithms, and remote sensing telemetry data processing for lunar and earth observation missions.",
                "location": "SAC Campus, Ahmedabad / NRSC Hyderabad",
                "venue_address": "Space Applications Centre (ISRO), Jodhpur Tekra, Ambawadi Vistar P.O., Ahmedabad, Gujarat 380015",
                "is_remote": False,
                "event_mode": "Offline (On-Site)",
                "event_date": "Jan 2026 - June 2026 (6 Months)",
                "registration_fee": "Free",
                "team_size": "Individual",
                "stipend_salary": "₹35,000/month + Subsidized ISRO Hostel",
                "prize_details": "Official ISRO Research Project Certificate & priority Scientist/Engineer-SC interview endorsement.",
                "duration": "6 Months",
                "perks": ["Official ISRO Research Project Certification", "Access to Real-time Satellite Telemetry Datasets", "Mentorship from Senior ISRO Scientists", "Campus Accommodation provided"],
                "schedule": [
                    {"phase": "Application & NOC Submission", "date": "Oct 25, 2026"},
                    {"phase": "Merit List Publication", "date": "Nov 15, 2026"},
                    {"phase": "Reporting & Security Clearance", "date": "Jan 05, 2026"}
                ],
                "deadline": now + timedelta(days=21),
                "apply_url": "https://www.isro.gov.in/Internships.html",
                "contact_email": "sac-internship@isro.gov.in",
                "required_skills": ["Python", "C++", "Machine Learning", "Deep Learning", "Data Structures & Algorithms"],
                "eligibility_criteria": "B.Tech/M.Tech students with minimum 8.0 CGPA and valid college NOC. Indian nationals only.",
                "experience_level": "Undergraduate / Postgraduate"
            },

            # =========================================================================
            # 3. GRADUATE & ENTRY-LEVEL JOBS
            # =========================================================================
            {
                "title": "Associate Software Development Engineer (Graduates 2026)",
                "company_name": "Atlassian",
                "opportunity_type": "job",
                "category_slug": "software-engineering",
                "organizer_type": "Tech Company",
                "description": "Build high-impact enterprise collaboration software (Jira, Confluence, Loom) used by over 300,000 companies. Design scalable microservices, reactive UI components, and AWS cloud native platforms.",
                "location": "Bengaluru, India / Global Remote",
                "venue_address": "Atlassian India, Divyasree TechPark, EPIP Zone, Whitefield, Bengaluru, Karnataka 560066",
                "is_remote": True,
                "event_mode": "Remote / Hybrid",
                "event_date": "Full-Time Joining July 2026",
                "registration_fee": "Free",
                "team_size": "Individual",
                "stipend_salary": "₹24 - ₹30 LPA Base + Equity (RSUs)",
                "prize_details": "Comprehensive New Grad compensation package including ₹1,50,000 WFH allowance and $2,000 annual learning stipend.",
                "duration": "Full-Time Permanent",
                "perks": ["Flexible Working (WFH or Modern Office)", "Annual Learning & Growth Stipend (₹1,50,000)", "Comprehensive Family Health Insurance", "Stock Grants (RSUs)"],
                "schedule": [
                    {"phase": "Application Closes", "date": "Oct 31, 2026"},
                    {"phase": "Online Technical Test (Karat)", "date": "Nov 10, 2026"},
                    {"phase": "Final Round Interviews (System + Values)", "date": "Nov 25, 2026"}
                ],
                "deadline": now + timedelta(days=28),
                "apply_url": "https://www.atlassian.com/company/careers/graduates",
                "contact_email": "gradrecruiting@atlassian.com",
                "required_skills": ["Java", "TypeScript", "React", "SQL", "AWS", "REST APIs", "Git"],
                "eligibility_criteria": "Graduating batch 2025 or 2026 with degree in CS, IT, Software Engineering or related discipline. No active backlogs.",
                "experience_level": "Entry Level (0-1 yrs)"
            },
            {
                "title": "Software Engineer — Digital Media Platforms",
                "company_name": "Adobe",
                "opportunity_type": "job",
                "category_slug": "software-engineering",
                "organizer_type": "Tech Company",
                "description": "Develop high-performance graphics engines, WebAssembly pipelines, and creative AI features powering Photoshop Web and Adobe Creative Cloud.",
                "location": "Noida / Bengaluru, India (Hybrid)",
                "venue_address": "Adobe Systems India Pvt Ltd, Plot No. A-14, Sector 132, Noida, Uttar Pradesh 201304",
                "is_remote": False,
                "event_mode": "Hybrid",
                "event_date": "Full-Time Starting 2026",
                "registration_fee": "Free",
                "team_size": "Individual",
                "stipend_salary": "₹22 - ₹28 LPA + Stock Bonuses",
                "prize_details": "Full-time position with sign-on bonus, stock units, and worldwide patent filing bonuses.",
                "duration": "Full-Time Permanent",
                "perks": ["Creative Cloud Full Subscription Free", "Patent Incentive Awards ($2,500/patent)", "Global Wellness Days off", "Health & Dental Coverage"],
                "schedule": [
                    {"phase": "Online Assessment", "date": "Nov 04, 2026"},
                    {"phase": "Technical Coding Interviews", "date": "Nov 18, 2026"}
                ],
                "deadline": now + timedelta(days=32),
                "apply_url": "https://www.adobe.com/careers/university.html",
                "contact_email": "indiauniversity@adobe.com",
                "required_skills": ["C++", "JavaScript", "TypeScript", "React", "Data Structures & Algorithms"],
                "eligibility_criteria": "B.Tech/M.Tech/Dual Degree in Computer Science with min. 7.5 CGPA.",
                "experience_level": "Entry Level (0-1 yrs)"
            },
            {
                "title": "Full Stack Software Engineer (Payments Core)",
                "company_name": "Razorpay",
                "opportunity_type": "job",
                "category_slug": "software-engineering",
                "organizer_type": "Tech Company",
                "description": "Build high-availability payment gateways, checkout SDKs, and merchant onboarding flows handling over 50,000 requests/second with 99.999% uptime.",
                "location": "Koramangala, Bengaluru (Hybrid)",
                "venue_address": "Razorpay HQ, SJR Cyber, Hosur Road, Laskar Hosur Rd, Koramangala, Bengaluru, Karnataka 560030",
                "is_remote": False,
                "event_mode": "Hybrid",
                "event_date": "Full-Time Joining 2026",
                "registration_fee": "Free",
                "team_size": "Individual",
                "stipend_salary": "₹18 - ₹24 LPA + ESOPs",
                "prize_details": "Competitive base + performance bonus + liquid ESOPs pool.",
                "duration": "Full-Time",
                "perks": ["Generous ESOP Grants", "Free Comprehensive Meals & Snacks", "Annual Tech Conference Pass Sponsored", "Health Insurance covering Parents"],
                "schedule": [
                    {"phase": "Application Review", "date": "Oct 24, 2026"},
                    {"phase": "Machine Coding Round (2 Hours)", "date": "Nov 06, 2026"},
                    {"phase": "System Architecture & Fit Round", "date": "Nov 16, 2026"}
                ],
                "deadline": now + timedelta(days=19),
                "apply_url": "https://razorpay.com/jobs",
                "contact_email": "careers@razorpay.com",
                "required_skills": ["React", "Node.js", "PostgreSQL", "Redis", "Docker", "REST APIs"],
                "eligibility_criteria": "2025/2026 batch engineering graduates with proven full-stack project building track record.",
                "experience_level": "Entry Level"
            },
            {
                "title": "Junior Cloud Infrastructure SDE",
                "company_name": "Oracle Cloud Infrastructure (OCI)",
                "opportunity_type": "job",
                "category_slug": "cloud-devops",
                "organizer_type": "Tech Company",
                "description": "Develop and operate next-generation distributed bare-metal cloud infrastructure, hypervisor management layers, and virtual networking stacks.",
                "location": "Hyderabad / Bengaluru, India",
                "venue_address": "Oracle India Pvt Ltd, Oracle Tech Hub, HITEC City, Hyderabad, Telangana 500081",
                "is_remote": False,
                "event_mode": "Hybrid",
                "event_date": "Full-Time 2026",
                "registration_fee": "Free",
                "team_size": "Individual",
                "stipend_salary": "₹20 - ₹26 LPA",
                "prize_details": "Competitive CTC package + Relocation + Performance Bonus.",
                "duration": "Full-Time Permanent",
                "perks": ["Oracle Global Certification Vouchers Free", "Relocation Assistance Provided", "Hybrid Work Model", "Health and Life Cover"],
                "schedule": [
                    {"phase": "Online Coding Challenge", "date": "Nov 02, 2026"},
                    {"phase": "Technical Loop (Linux, DSA, OS)", "date": "Nov 14, 2026"}
                ],
                "deadline": now + timedelta(days=25),
                "apply_url": "https://www.oracle.com/corporate/careers",
                "contact_email": "oci-recruiting@oracle.com",
                "required_skills": ["Java", "C++", "Linux", "Docker", "Kubernetes", "System Design"],
                "eligibility_criteria": "B.Tech/M.Tech in CS/IT/ECE graduating in 2025/2026.",
                "experience_level": "Entry Level"
            },

            # =========================================================================
            # 4. CERTIFICATIONS
            # =========================================================================
            {
                "title": "AWS Certified Solutions Architect — Associate (SAA-C03)",
                "company_name": "Amazon Web Services",
                "opportunity_type": "certification",
                "category_slug": "certifications",
                "organizer_type": "Cloud Provider",
                "description": "Industry-standard credential validating your ability to design secure, robust, highly available, and cost-optimized distributed systems on AWS.",
                "location": "Online Proctored / Pearson VUE Testing Centers",
                "venue_address": "Online Proctored via Pearson VUE or Authorized Testing Centers Worldwide",
                "is_remote": True,
                "event_mode": "Online Exam",
                "event_date": "Year-Round / Self-Scheduled Exam",
                "registration_fee": "50% Off Voucher for Students ($75 / Free via AWS Educate)",
                "team_size": "Individual",
                "stipend_salary": "Valued Credential (Boosts Resume ATS by 35%)",
                "prize_details": "Digital Badge on Credly, direct verification on LinkedIn, and priority consideration in AWS Partner Network recruitment drives.",
                "duration": "4 to 6 Weeks Recommended Study Time (50 Hours)",
                "perks": ["Globally Recognized Digital Credential", "Direct LinkedIn Verification Badge", "Priority Access to AWS Partner Job Boards", "50% Discount on Next Exam"],
                "schedule": [
                    {"phase": "Study Week 1-2: Core VPC, IAM & EC2", "date": "Ongoing"},
                    {"phase": "Study Week 3-4: S3, DynamoDB, RDS & Lambda", "date": "Ongoing"},
                    {"phase": "Practice Exams & Pearson VUE Booking", "date": "Ongoing"}
                ],
                "deadline": now + timedelta(days=90),
                "apply_url": "https://aws.amazon.com/certification/certified-solutions-architect-associate/",
                "contact_email": "aws-certification@amazon.com",
                "required_skills": ["AWS", "Docker", "System Design", "SQL", "Linux"],
                "eligibility_criteria": "Open to all students and software professionals. Student discount available with .edu / college email.",
                "experience_level": "Intermediate"
            },
            {
                "title": "Google Cloud Professional Data Engineer",
                "company_name": "Google Cloud",
                "opportunity_type": "certification",
                "category_slug": "certifications",
                "organizer_type": "Cloud Provider",
                "description": "Demonstrate your ability to design, build, operationalize, and secure data processing systems, ETL pipelines, BigQuery analytics, and Vertex AI models on GCP.",
                "location": "Online Exam / Kryterion Test Centers",
                "venue_address": "Kryterion Global Test Center Network & Online Biometric Proctored",
                "is_remote": True,
                "event_mode": "Online Exam",
                "event_date": "Year-Round / Self-Scheduled",
                "registration_fee": "₹12,000 (50% Student Discount Available)",
                "team_size": "Individual",
                "stipend_salary": "Top Industry Credential for Data Engineers",
                "prize_details": "Google Cloud Certified Directory Listing, exclusive Google Cloud Certified swag jacket, and Google Cloud Partner invitations.",
                "duration": "6 to 8 Weeks Prep (60 Hours)",
                "perks": ["Google Cloud Certified Official Swag Jacket", "Listing on Google Cloud Certified Directory", "Google Cloud Next Conference VIP Pass", "Credly Digital Badge"],
                "schedule": [
                    {"phase": "Phase 1: BigQuery & Cloud Storage Optimization", "date": "Self-Paced"},
                    {"phase": "Phase 2: Dataflow (Apache Beam) & Pub/Sub Streaming", "date": "Self-Paced"},
                    {"phase": "Phase 3: Vertex AI & Cloud Dataproc", "date": "Self-Paced"}
                ],
                "deadline": now + timedelta(days=75),
                "apply_url": "https://cloud.google.com/certification/data-engineer",
                "contact_email": "gcp-certification@google.com",
                "required_skills": ["Google Cloud", "SQL", "Python", "Data Structures & Algorithms", "PostgreSQL"],
                "eligibility_criteria": "Recommended for students with foundational database, SQL, and data pipeline knowledge.",
                "experience_level": "Intermediate / Advanced"
            },
            {
                "title": "CKA: Certified Kubernetes Administrator",
                "company_name": "Linux Foundation & CNCF",
                "opportunity_type": "certification",
                "category_slug": "certifications",
                "organizer_type": "Global Community",
                "description": "100% hands-on performance-based exam proving your competency to configure, administer, troubleshoot, and scale production Kubernetes clusters.",
                "location": "Online Performance-Based Exam",
                "venue_address": "Linux Foundation Remote Proctored Terminal Sandbox",
                "is_remote": True,
                "event_mode": "Online Exam",
                "event_date": "Anytime within 12 months of registration",
                "registration_fee": "$395 (Student discount code 'KUBEEDU' gives 25% off)",
                "team_size": "Individual",
                "stipend_salary": "Gold Standard DevOps Credential",
                "prize_details": "CNCF Certified Administrator Credential + 2 Exam Attempts included.",
                "duration": "6 to 8 Weeks Hands-on Lab Prep",
                "perks": ["2 Exam Attempts Included with Purchase", "Access to Killer.sh Practice Simulation Labs", "Official CNCF Digital Certificate & Badge"],
                "schedule": [
                    {"phase": "Cluster Architecture & ETCD Backup", "date": "Prep Week 1"},
                    {"phase": "Workloads, Pods, Deployments & DaemonSets", "date": "Prep Week 2"},
                    {"phase": "Networking, Ingress & NetworkPolicies", "date": "Prep Week 3"},
                    {"phase": "Storage, PV/PVCs & Troubleshooting", "date": "Prep Week 4"}
                ],
                "deadline": now + timedelta(days=60),
                "apply_url": "https://www.cncf.io/certification/cka/",
                "contact_email": "certifications@linuxfoundation.org",
                "required_skills": ["Docker", "Kubernetes", "Linux", "CI/CD", "Git"],
                "eligibility_criteria": "Familiarity with Linux command line and containerization fundamentals.",
                "experience_level": "Intermediate / Advanced"
            },

            # =========================================================================
            # 5. COURSES
            # =========================================================================
            {
                "title": "CS50x: Introduction to Computer Science",
                "company_name": "Harvard University",
                "opportunity_type": "course",
                "category_slug": "software-engineering",
                "organizer_type": "College / University",
                "description": "Harvard's world-renowned flagship course on computer science and the art of programming. Master computational thinking, C memory allocation, Python, SQL, web servers, and capstone project development.",
                "location": "Harvard Online / edX Platform",
                "venue_address": "Harvard University Division of Continuing Education, 51 Brattle Street, Cambridge, MA 02138",
                "is_remote": True,
                "event_mode": "Online Self-Paced",
                "event_date": "Self-Paced (Available Year-Round)",
                "registration_fee": "100% Free (Free Verified Certificate via CS50 portal)",
                "team_size": "Individual",
                "stipend_salary": "Free (Includes CS50 Certificate of Completion)",
                "prize_details": "Free official certificate signed by Prof. David J. Malan upon scoring 70%+ on all 10 problem sets.",
                "duration": "10 to 12 Weeks (6-9 Hours/Week)",
                "perks": ["Official CS50 Certificate from HarvardX", "Hands-on Capstone Portfolio Project", "Access to Global CS50 Discord Community", "Comprehensive Problem Set Code Reviews"],
                "schedule": [
                    {"phase": "Weeks 0-5: C, Algorithms, Memory & Data Structures", "date": "Self-Paced"},
                    {"phase": "Weeks 6-8: Python, SQL & Flask Backend", "date": "Self-Paced"},
                    {"phase": "Weeks 9-10: HTML/CSS, JavaScript & Final Capstone", "date": "Self-Paced"}
                ],
                "deadline": now + timedelta(days=120),
                "apply_url": "https://pll.harvard.edu/course/cs50-introduction-computer-science",
                "contact_email": "cs50@harvard.edu",
                "required_skills": ["Python", "C++", "SQL", "Flask", "Data Structures & Algorithms"],
                "eligibility_criteria": "Open to all students worldwide. Beginner-friendly with no prior prerequisites.",
                "experience_level": "Beginner / Intermediate"
            },
            {
                "title": "Machine Learning Specialization",
                "company_name": "Stanford Online & DeepLearning.AI",
                "opportunity_type": "course",
                "category_slug": "data-science-ai",
                "organizer_type": "College / University",
                "description": "Master core machine learning algorithms, supervised regression, decision trees, neural network backpropagation, and reinforcement learning taught by AI pioneer Andrew Ng.",
                "location": "Coursera Platform",
                "venue_address": "Stanford University & DeepLearning.AI, Stanford, CA 94305",
                "is_remote": True,
                "event_mode": "Online",
                "event_date": "Self-Paced (Enroll Anytime)",
                "registration_fee": "Free Audit / 100% Financial Aid Available",
                "team_size": "Individual",
                "stipend_salary": "Free Audit Available",
                "prize_details": "Stanford Online & DeepLearning.AI Certificate of Specialization.",
                "duration": "12 Weeks (4-6 Hours/Week)",
                "perks": ["Certificate signed by Andrew Ng", "Practical NumPy and PyTorch Lab Assignments", "Resume-ready Machine Learning Projects"],
                "schedule": [
                    {"phase": "Course 1: Supervised ML (Regression & Classification)", "date": "Self-Paced"},
                    {"phase": "Course 2: Advanced Learning Algorithms (Neural Networks)", "date": "Self-Paced"},
                    {"phase": "Course 3: Unsupervised Learning, Recommenders & RL", "date": "Self-Paced"}
                ],
                "deadline": now + timedelta(days=80),
                "apply_url": "https://www.coursera.org/specializations/machine-learning-introduction",
                "contact_email": "support@deeplearning.ai",
                "required_skills": ["Python", "Machine Learning", "Data Structures & Algorithms", "Deep Learning"],
                "eligibility_criteria": "Basic familiarity with high school mathematics (algebra) and Python syntax.",
                "experience_level": "Beginner / Intermediate"
            },

            # =========================================================================
            # 6. COMPETITIONS & CODING CONTESTS
            # =========================================================================
            {
                "title": "TCS CodeVita Season 13 — Global Coding Contest",
                "company_name": "Tata Consultancy Services",
                "opportunity_type": "competition",
                "category_slug": "competitions-hackathons",
                "organizer_type": "Tech Company",
                "description": "Guinness World Record holding algorithmic coding contest. Compete with 100,000+ collegiate programmers across the globe. Solve algorithmic puzzles under strict time limits.",
                "location": "Online Rounds + Mumbai Grand Finale",
                "venue_address": "TCS Olympus Centre, Rodas Enclave, Park Avenue, Hiranandani Estate, Thane, Maharashtra 400607",
                "is_remote": False,
                "event_mode": "Hybrid (Online Prelims + In-Person Finale)",
                "event_date": "November 20 - 22, 2026",
                "registration_fee": "Free",
                "team_size": "Individual (Solo)",
                "stipend_salary": "₹15,00,000 Cash Pool + Direct SDE Job Offers",
                "prize_details": "1st Prize: $10,000 (₹8.3 Lakhs) • 2nd: $7,000 • 3rd: $3,000 • Direct TCS Digital (₹7.5 LPA) & TCS Innovator (₹11.5 LPA) interview calls for Top 1000 coders.",
                "duration": "6-Hour Coding Round (Prelims) + 8-Hour Grand Finale",
                "perks": ["Direct Interview Call for TCS Digital & Innovator Roles", "Guinness Record Participation Certificate", "All-expenses paid trip to Mumbai for Finalists", "TCS CodeVita Trophy"],
                "schedule": [
                    {"phase": "Registration Closes", "date": "Oct 18, 2026"},
                    {"phase": "Mock Coding Challenge", "date": "Oct 25, 2026"},
                    {"phase": "Round 1: National Qualifier (6 Hours)", "date": "Nov 07, 2026"},
                    {"phase": "Grand Finale in Mumbai", "date": "Nov 20 - 22, 2026"}
                ],
                "deadline": now + timedelta(days=7),
                "apply_url": "https://campuscommune.tcs.com/en-in/intro/contests/codevita",
                "contact_email": "codevita@tcs.com",
                "required_skills": ["Data Structures & Algorithms", "C++", "Java", "Python"],
                "eligibility_criteria": "All college students graduating in years 2025, 2026, 2027, 2028 across recognized academic institutions worldwide.",
                "experience_level": "All Levels"
            },
            {
                "title": "Kaggle LLM 2026 Science Grand Challenge",
                "company_name": "Kaggle & Google DeepMind",
                "opportunity_type": "competition",
                "category_slug": "data-science-ai",
                "organizer_type": "Tech Company",
                "description": "Build high-accuracy Question-Answering and scientific reasoning models benchmarked against STEM datasets. Compete for Kaggle Grandmaster points and cash awards.",
                "location": "Online (Kaggle Platform)",
                "venue_address": "Kaggle Platform Submissions Hub",
                "is_remote": True,
                "event_mode": "Online",
                "event_date": "October 15 - December 15, 2026",
                "registration_fee": "Free",
                "team_size": "1 to 5 Members",
                "stipend_salary": "Prizes: $100,000 Cash Pool",
                "prize_details": "1st: $40,000 • 2nd: $25,000 • 3rd: $15,000 • 4th: $10,000 • 5th: $10,000 + Kaggle Gold Medals.",
                "duration": "2 Months",
                "perks": ["Kaggle Competition Gold/Silver/Bronze Medals", "Google Cloud TPU Compute Credits", "Direct Visibility to Top AI Labs globally"],
                "schedule": [
                    {"phase": "Competition Launch", "date": "Oct 15, 2026"},
                    {"phase": "Team Merger Deadline", "date": "Nov 20, 2026"},
                    {"phase": "Final Submission Deadline", "date": "Dec 15, 2026"}
                ],
                "deadline": now + timedelta(days=35),
                "apply_url": "https://www.kaggle.com/competitions",
                "contact_email": "support@kaggle.com",
                "required_skills": ["Python", "PyTorch", "Deep Learning", "Machine Learning"],
                "eligibility_criteria": "Free Kaggle account registration.",
                "experience_level": "Intermediate / Advanced"
            },

            # =========================================================================
            # 7. WORKSHOPS & MASTERCLASSES
            # =========================================================================
            {
                "title": "Generative AI & Autonomous Agents Hands-on Masterclass",
                "company_name": "Google Developer Groups (GDG) Bangalore",
                "opportunity_type": "workshop",
                "category_slug": "workshops",
                "organizer_type": "Global Community",
                "description": "A deep dive hands-on workshop building production-ready autonomous multi-agent systems with Gemini 2.0 API, Function Calling, LangGraph, and Vector Databases.",
                "location": "WeWork Galaxy, Residency Road, Bangalore & Live Stream",
                "venue_address": "WeWork Galaxy, 43, Residency Rd, Shanthala Nagar, Ashok Nagar, Bengaluru, Karnataka 560025",
                "is_remote": False,
                "event_mode": "Hybrid (In-Person + Live Stream)",
                "event_date": "Saturday, October 24, 2026 (10:00 AM - 5:00 PM IST)",
                "registration_fee": "Free RSVP (Limited to 250 in-person seats)",
                "team_size": "Individual",
                "stipend_salary": "Free Workshop + Certificate & Lunch",
                "prize_details": "Official GDG Certificate of Completion + $100 Google Cloud Credits for all attendees.",
                "duration": "1 Full Day (7 Hours Hands-on)",
                "perks": ["Official GDG Certificate of Attendance", "$100 Google Cloud API Credits", "Complimentary Lunch & GDG Swag Pack", "Networking with Google Developer Experts (GDEs)"],
                "schedule": [
                    {"phase": "10:00 AM: Keynote on Gemini 2.0 Multimodal Architecture", "date": "Oct 24, 2026"},
                    {"phase": "11:30 AM: Live Code Along: Building Agentic Workflows", "date": "Oct 24, 2026"},
                    {"phase": "02:00 PM: Vector Databases & RAG Optimization", "date": "Oct 24, 2026"},
                    {"phase": "04:00 PM: Capstone Project Showcase & Q&A", "date": "Oct 24, 2026"}
                ],
                "deadline": now + timedelta(days=5),
                "apply_url": "https://gdg.community.dev",
                "contact_email": "organizers@gdgbangalore.org",
                "required_skills": ["Python", "FastAPI", "Machine Learning", "REST APIs", "Git"],
                "eligibility_criteria": "Open to all engineering students, developers, and tech enthusiasts. Basic Python knowledge required.",
                "experience_level": "All Levels"
            },
            {
                "title": "Full-Stack System Design & Scalable Architecture Bootcamp",
                "company_name": "Devfolio & AWS Community India",
                "opportunity_type": "workshop",
                "category_slug": "workshops",
                "organizer_type": "Tech Company",
                "description": "Intensive weekend masterclass teaching high-concurrency microservices design, database sharding, Redis caching strategies, Kafka event streaming, and CI/CD deployment pipelines.",
                "location": "Interactive Virtual Zoom & Discord Stage",
                "venue_address": "Live Streamed on Discord Stage & Zoom Interactive Rooms",
                "is_remote": True,
                "event_mode": "Online (Interactive Virtual)",
                "event_date": "October 31 - November 01, 2026 (Weekend 10 AM - 4 PM)",
                "registration_fee": "Free",
                "team_size": "Individual",
                "stipend_salary": "Free Bootcamp",
                "prize_details": "Digital Certificate of Completion + System Design Cheatsheet & Architecture Blueprint PDF.",
                "duration": "2 Days (12 Hours Total)",
                "perks": ["Certificate of Masterclass Completion", "Curated System Design Blueprint Book (PDF)", "Access to Private Discord Architecture Channel"],
                "schedule": [
                    {"phase": "Day 1: Microservices, Load Balancing & DB Sharding", "date": "Oct 31, 2026"},
                    {"phase": "Day 2: Kafka Streaming, Caching & Live Architecture Mock", "date": "Nov 01, 2026"}
                ],
                "deadline": now + timedelta(days=9),
                "apply_url": "https://devfolio.co/workshops",
                "contact_email": "workshops@devfolio.co",
                "required_skills": ["System Design", "SQL", "Docker", "REST APIs", "Redis"],
                "eligibility_criteria": "Engineering students preparing for Tier-1 product company technical interviews.",
                "experience_level": "Intermediate"
            }
        ]

        print(f"[*] Seeding/Updating {len(opportunities_data)} real-world opportunities...")
        for item in opportunities_data:
            existing = Opportunity.query.filter_by(title=item['title'], company_name=item['company_name']).first()
            category = cat_objs.get(item.get('category_slug'))
            
            if not existing:
                opp = Opportunity(
                    title=item['title'],
                    company_name=item['company_name'],
                    opportunity_type=item['opportunity_type'],
                    category_id=category.id if category else None,
                    organizer_type=item.get('organizer_type', 'Company'),
                    description=item['description'],
                    location=item['location'],
                    venue_address=item.get('venue_address', item['location']),
                    is_remote=item['is_remote'],
                    event_mode=item.get('event_mode', 'Online'),
                    event_date=item.get('event_date'),
                    registration_fee=item.get('registration_fee', 'Free'),
                    team_size=item.get('team_size'),
                    stipend_salary=item.get('stipend_salary'),
                    prize_details=item.get('prize_details'),
                    duration=item.get('duration'),
                    perks=item.get('perks', []),
                    schedule=item.get('schedule', []),
                    deadline=item['deadline'],
                    apply_url=item['apply_url'],
                    contact_email=item.get('contact_email'),
                    required_skills=item['required_skills'],
                    eligibility_criteria=item['eligibility_criteria'],
                    status='active',
                    experience_level=item['experience_level']
                )
                db.session.add(opp)
            else:
                existing.category_id = category.id if category else existing.category_id
                existing.organizer_type = item.get('organizer_type', existing.organizer_type)
                existing.description = item['description']
                existing.location = item['location']
                existing.venue_address = item.get('venue_address', existing.venue_address)
                existing.is_remote = item['is_remote']
                existing.event_mode = item.get('event_mode', existing.event_mode)
                existing.event_date = item.get('event_date', existing.event_date)
                existing.registration_fee = item.get('registration_fee', existing.registration_fee)
                existing.team_size = item.get('team_size', existing.team_size)
                existing.stipend_salary = item.get('stipend_salary', existing.stipend_salary)
                existing.prize_details = item.get('prize_details', existing.prize_details)
                existing.duration = item.get('duration', existing.duration)
                existing.perks = item.get('perks', [])
                existing.schedule = item.get('schedule', [])
                existing.deadline = item['deadline']
                existing.apply_url = item['apply_url']
                existing.contact_email = item.get('contact_email', existing.contact_email)
                existing.required_skills = item['required_skills']
                existing.eligibility_criteria = item['eligibility_criteria']
                existing.status = 'active'
                existing.experience_level = item['experience_level']

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
                ("REST APIs", "advanced", 2.5),
                ("Data Structures & Algorithms", "advanced", 3.0)
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

            # Student Projects
            project1 = StudentProject(
                student_id=profile.id,
                title="Career DNA AI — Intelligent Opportunity Platform",
                description="AI-driven career matching platform and student opportunity engine using Flask, PyMySQL, and Gemini AI.",
                tech_stack="Python, Flask, JavaScript, MySQL, Docker, REST APIs",
                github_url="https://github.com/alexmorgan-dev/career-dna-ai",
                live_url="https://careerdna.ai",
                role="Lead Full-Stack Developer"
            )
            project2 = StudentProject(
                student_id=profile.id,
                title="CloudStream Distributed Event Pipeline",
                description="High-throughput real-time telemetry processing pipeline capable of handling 50k events/sec with Redis and Docker.",
                tech_stack="Go, Redis, Docker, PostgreSQL, React",
                github_url="https://github.com/alexmorgan-dev/cloudstream",
                live_url="https://cloudstream.dev",
                role="Backend Architect"
            )
            db.session.add(project1)
            db.session.add(project2)

            # Student Certifications
            cert1 = StudentCertification(
                student_id=profile.id,
                title="AWS Certified Cloud Practitioner",
                issuing_organization="Amazon Web Services",
                issue_date="2025-05",
                credential_id="AWS-CCP-982341",
                credential_url="https://aws.amazon.com/verify"
            )
            db.session.add(cert1)

            # Pre-seed sample applications
            opp_google = Opportunity.query.filter_by(company_name="Google").first()
            if opp_google:
                app1 = Application(
                    student_id=profile.id,
                    opportunity_id=opp_google.id,
                    company_name="Google",
                    position_title=opp_google.title,
                    opportunity_type="internship",
                    status="applied",
                    applied_date=datetime.utcnow().date(),
                    salary_offered="₹1,25,000/month",
                    notes="Applied via Career DNA AI portal with tailored ATS resume."
                )
                db.session.add(app1)

            opp_hackmit = Opportunity.query.filter_by(title="HackMIT 2026").first()
            if opp_hackmit:
                app2 = Application(
                    student_id=profile.id,
                    opportunity_id=opp_hackmit.id,
                    company_name="MIT Tech Club",
                    position_title="HackMIT 2026",
                    opportunity_type="hackathon",
                    status="registered",
                    applied_date=datetime.utcnow().date(),
                    salary_offered="Prizes: $50,000",
                    notes="Registered team: AlgoKnights for AI track."
                )
                db.session.add(app2)

        db.session.commit()
        print("[+] Database seeding completed successfully with 33+ comprehensive opportunities!")

if __name__ == '__main__':
    seed_database()
