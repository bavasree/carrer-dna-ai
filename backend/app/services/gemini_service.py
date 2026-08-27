import json
import logging
import os
import re
import time

logger = logging.getLogger('career_dna_ai.gemini')
logger.setLevel(logging.INFO)

class GeminiService:
    """
    Centralized Google Gemini AI Service.
    Handles all LLM interactions with multi-model fallback waterfall,
    strict per-request timeouts, defensive JSON parsing, and high-fidelity
    student-personalized algorithmic generators.
    """

    AVAILABLE_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', '').strip()
        self.genai = None
        self.active_model_name = None
        self._initialize_gemini()

    def _initialize_gemini(self):
        """Initializes the Google Generative AI SDK client if API key is provided."""
        # Re-check environment variable in case it was loaded late
        if not self.api_key:
            self.api_key = os.getenv('GEMINI_API_KEY', '').strip()

        if not self.api_key:
            logger.info("No GEMINI_API_KEY found. GeminiService operating in high-fidelity heuristic mode.")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.genai = genai
            self.active_model_name = "gemini-1.5-flash"
            logger.info(f"Google Gemini SDK successfully configured with API Key (Prefix: {self.api_key[:6]}...)")
        except Exception as e:
            logger.warning(f"Failed to initialize Google Gemini client: {e}. Operating in heuristic mode.")
            self.genai = None

    def _clean_and_parse_json(self, raw_text, default_fallback):
        """
        Defensively cleans markdown fences, trailing commas, and parses string into JSON dict or list.
        """
        if not raw_text:
            return default_fallback

        cleaned = str(raw_text).strip()
        # Remove ```json ... ``` or ``` ... ``` wrappers
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Attempt to extract outermost { ... } or [ ... ]
        try:
            dict_match = re.search(r'(\{[\s\S]*\})', cleaned)
            if dict_match:
                return json.loads(dict_match.group(1))
        except Exception:
            pass

        try:
            list_match = re.search(r'(\[[\s\S]*\])', cleaned)
            if list_match:
                return json.loads(list_match.group(1))
        except Exception:
            pass

        logger.warning(f"Could not parse valid JSON from AI response: {cleaned[:150]}...")
        return default_fallback

    def _call_gemini_raw(self, prompt, retries=1):
        """
        Executes a Gemini API call with multi-model fallback and strict 10s timeout
        to prevent any hanging requests.
        """
        if not self.api_key:
            self._initialize_gemini()

        if not self.genai or not self.api_key:
            return None

        # Try active model first, then remaining models
        models_to_try = [self.active_model_name] if self.active_model_name else []
        for m in self.AVAILABLE_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        for model_name in models_to_try:
            try:
                model = self.genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.25,
                        "top_p": 0.95,
                    }
                )
                start_time = time.time()
                # Request options with strict timeout of 10 seconds
                response = model.generate_content(
                    prompt,
                    request_options={"timeout": 10}
                )
                duration = time.time() - start_time
                if response and response.text:
                    logger.info(f"Gemini API ({model_name}) answered in {duration:.2f}s")
                    self.active_model_name = model_name
                    return response.text
            except Exception as e:
                logger.info(f"Gemini model {model_name} call skipped: {e}")
                continue

        return None

    # ==========================================
    # 1. AI Career Analysis & Readiness Score
    # ==========================================
    def analyze_career(self, profile_data):
        """
        Performs comprehensive career readiness, strengths, weaknesses,
        skill gaps, and target role suggestions.
        """
        skills_str = json.dumps([s.get('skill_name') for s in profile_data.get('skills', [])])
        projects_str = json.dumps([p.get('title') + ' (' + str(p.get('tech_stack', '')) + ')' for p in profile_data.get('projects', [])])
        certs_str = json.dumps([c.get('title') for c in profile_data.get('certifications', [])])

        prompt = f"""
You are an expert AI Career Coach for university students. Analyze the following student profile and return a JSON object with:
1. "readiness_score": integer from 0 to 100 representing overall readiness for their target career/industry.
2. "strengths": list of 3-5 strings highlighting technical & academic strong points.
3. "weaknesses": list of 2-4 strings indicating areas for growth.
4. "skill_gaps": list of 3-6 specific high-demand skills missing for their target career goal.
5. "recommended_roles": list of 3-5 specific job/internship roles that match their profile.
6. "recommended_certifications": list of 3-4 industry certifications that would maximize their profile.
7. "recommended_technologies": list of 4-6 modern frameworks/tools/languages they should learn next.
8. "ai_summary": a 2-3 sentence inspiring executive summary and diagnosis.

Student Profile:
- Full Name: {profile_data.get('full_name', 'Student')}
- Degree & Branch: {profile_data.get('degree', 'B.Tech')} in {profile_data.get('branch', 'Computer Science')} (Graduation: {profile_data.get('graduation_year', '2026')})
- College: {profile_data.get('college_name', 'University')}
- CGPA: {profile_data.get('cgpa', '8.0')}
- Career Goal: {profile_data.get('career_goal', 'Software Engineer')}
- Target Role: {profile_data.get('target_role', 'Full-Stack Developer')}
- Verified Skills: {skills_str}
- Projects: {projects_str}
- Certifications: {certs_str}

Respond ONLY with valid JSON.
"""
        raw_res = self._call_gemini_raw(prompt)
        parsed = self._clean_and_parse_json(raw_res, None)
        if parsed and isinstance(parsed, dict) and 'readiness_score' in parsed:
            return parsed

        return self._fallback_career_analysis(profile_data)

    def _fallback_career_analysis(self, profile_data):
        """Rule-based and algorithmic career analysis fallback personalized to student."""
        skills = [s.get('skill_name', '').strip() for s in profile_data.get('skills', []) if s.get('skill_name')]
        skills_lower = [s.lower() for s in skills]
        projects = profile_data.get('projects', [])
        certs = profile_data.get('certifications', [])
        cgpa = profile_data.get('cgpa') or 7.5
        target = (profile_data.get('target_role') or profile_data.get('career_goal') or 'Software Engineer').strip()
        degree = profile_data.get('degree') or 'B.Tech'
        branch = profile_data.get('branch') or 'Computer Science'

        # Dynamic score calculation
        score = 45
        score += min(25, len(skills) * 3)
        score += min(20, len(projects) * 6)
        score += min(10, len(certs) * 5)
        if cgpa >= 8.5: score += 10
        elif cgpa >= 7.5: score += 7
        elif cgpa >= 6.5: score += 4
        score = min(96, max(35, score))

        strengths = []
        if len(skills) >= 3:
            strengths.append(f"Strong foundation in core technical competencies ({', '.join(skills[:3])}).")
        else:
            strengths.append("Demonstrated foundation in essential programming concepts.")

        if len(projects) >= 1:
            strengths.append(f"Hands-on project experience with practical implementations ({projects[0].get('title', 'Flagship Project')}).")
        else:
            strengths.append("Established academic coursework and project background.")

        if cgpa >= 7.5:
            strengths.append(f"Consistent academic track record with {cgpa} CGPA in {degree} ({branch}).")
        else:
            strengths.append(f"Active degree pursuit in {degree} ({branch}).")

        strengths.append("Clear career direction and eagerness to explore industry opportunities.")

        weaknesses = []
        if len(projects) < 2:
            weaknesses.append("Limited full-stack / end-to-end production projects deployed live.")
        if len(skills) < 6:
            weaknesses.append("Skill breadth is still narrow compared to competitive entry-level benchmarks.")
        weaknesses.append("Needs deeper exposure to system design, cloud containerization, and automated CI/CD.")

        target_lower = target.lower()
        if any(k in target_lower for k in ['data', 'ai', 'ml', 'machine learning', 'deep learning']):
            skill_gaps = ["PyTorch / TensorFlow", "MLOps & Model Deployment", "Apache Spark", "Docker & Kubernetes", "Advanced Feature Engineering"]
            rec_roles = ["Junior Machine Learning Engineer", "Data Scientist Intern", "AI Solutions Engineer", "Data Analyst", "Applied AI Developer"]
            rec_certs = ["AWS Certified Machine Learning - Specialty", "Google Cloud Professional Data Engineer", "DeepLearning.AI TensorFlow Developer"]
            rec_techs = ["PyTorch", "FastAPI", "Hugging Face", "MLflow", "PostgreSQL", "Docker"]
        elif any(k in target_lower for k in ['front', 'ui', 'react', 'web', 'javascript']):
            skill_gaps = ["Next.js & Server Components", "TypeScript Mastery", "Tailwind CSS & Micro-interactions", "Web Performance Optimization", "Jest & Cypress E2E Testing"]
            rec_roles = ["Frontend Developer Intern", "UI/UX Engineer", "React/Next.js Developer", "Web Application Developer"]
            rec_certs = ["Meta Front-End Developer Certificate", "AWS Certified Developer - Associate"]
            rec_techs = ["React 19", "Next.js", "TypeScript", "TailwindCSS", "Redux Toolkit", "GraphQL"]
        elif any(k in target_lower for k in ['cloud', 'devops', 'infra', 'sre']):
            skill_gaps = ["Kubernetes & Helm", "Terraform (IaC)", "CI/CD Pipelines (GitHub Actions)", "Linux Systems Administration", "Prometheus & Grafana"]
            rec_roles = ["Cloud Operations Intern", "DevOps Engineer Trainee", "Site Reliability Engineer", "Platform Engineer"]
            rec_certs = ["AWS Certified Solutions Architect", "CKA (Certified Kubernetes Administrator)", "HashiCorp Terraform Associate"]
            rec_techs = ["Terraform", "Docker", "Kubernetes", "AWS/GCP", "GitHub Actions", "Ansible"]
        else:
            skill_gaps = ["System Design & Microservices", "Docker Containerization", "CI/CD Deployment Pipelines", "Cloud Infrastructure (AWS/GCP)", "Redis Caching & Async Queues"]
            rec_roles = [f"Junior {target}", "Software Development Engineer Intern (SDE-1)", "Full-Stack Developer", "Backend Systems Engineer"]
            rec_certs = ["AWS Certified Solutions Architect - Associate", "Meta Full-Stack Professional", "Oracle Certified Associate Java"]
            rec_techs = ["Docker", "PostgreSQL", "FastAPI / Node.js", "Redis", "AWS Lambda", "Git & CI/CD"]

        return {
            "readiness_score": score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "skill_gaps": skill_gaps,
            "recommended_roles": rec_roles,
            "recommended_certifications": rec_certs,
            "recommended_technologies": rec_techs,
            "ai_summary": f"Your current profile demonstrates solid foundational momentum toward becoming a {target}. By targeting {skill_gaps[0]} and deploying a flagship capstone project, your market readiness will reach Tier-1 benchmarks."
        }

    # ==========================================
    # 2. AI Skill-Gap Analysis
    # ==========================================
    def analyze_skill_gap(self, profile_data, target_role):
        """Analyzes exact missing competencies and learning plan for a specific role."""
        skills_str = json.dumps([s.get('skill_name') for s in profile_data.get('skills', [])])
        projects_str = json.dumps([p.get('title') for p in profile_data.get('projects', [])])

        prompt = f"""
Compare this student's skills against modern industry requirements for the role of "{target_role}".
Return JSON with:
1. "target_role": "{target_role}"
2. "matched_skills": list of strings that student already has that are relevant.
3. "missing_critical_skills": list of 3-5 mandatory skills for this role they lack.
4. "missing_nice_to_have_skills": list of 2-4 supplementary skills.
5. "estimated_time_to_close_gap": string (e.g. "6-8 weeks of focused study")
6. "recommended_learning_path": list of 3-4 actionable sequential steps.

Student Skills: {skills_str}
Student Experience/Projects: {projects_str}
"""
        raw_res = self._call_gemini_raw(prompt)
        parsed = self._clean_and_parse_json(raw_res, None)
        if parsed and isinstance(parsed, dict) and 'missing_critical_skills' in parsed:
            return parsed

        # Heuristic fallback
        user_skills = set(s.get('skill_name', '').lower() for s in profile_data.get('skills', []))
        role_skills_map = {
            'full stack': ['javascript', 'python', 'react', 'node.js', 'sql', 'docker', 'git', 'rest apis', 'html/css'],
            'data science': ['python', 'pandas', 'numpy', 'scikit-learn', 'sql', 'machine learning', 'data visualization', 'statistics'],
            'devops': ['linux', 'docker', 'kubernetes', 'aws', 'ci/cd', 'terraform', 'git', 'python', 'bash'],
            'ai engineer': ['python', 'pytorch', 'deep learning', 'nlp', 'llms', 'fastapi', 'vector databases', 'docker'],
            'frontend': ['javascript', 'typescript', 'react', 'html5', 'css3', 'tailwind css', 'redux', 'git'],
            'backend': ['python', 'sql', 'rest apis', 'docker', 'database design', 'microservices', 'redis', 'git']
        }
        
        matched_category = 'full stack'
        for k in role_skills_map:
            if k in target_role.lower():
                matched_category = k
                break
        
        target_skills = role_skills_map[matched_category]
        matched = [s for s in target_skills if any(us in s or s in us for us in user_skills)]
        missing_crit = [s.title() for s in target_skills if not any(us in s or s in us for us in user_skills)][:4]
        if not missing_crit:
            missing_crit = ["Advanced System Design", "Microservices Architecture", "Performance Profiling"]

        return {
            "target_role": target_role,
            "matched_skills": [m.title() for m in matched] if matched else ["Git", "Core Programming"],
            "missing_critical_skills": missing_crit,
            "missing_nice_to_have_skills": ["Cloud Monitoring & Logging", "Agile Workflow", "Automated Testing"],
            "estimated_time_to_close_gap": "6 to 8 weeks with 10 hrs/week practice",
            "recommended_learning_path": [
                f"Master core syntax and paradigms in {missing_crit[0]} through interactive tutorials.",
                f"Build a mini CRUD service integrating {missing_crit[min(1, len(missing_crit)-1)]}.",
                "Deploy project live on cloud with automated CI/CD pipeline.",
                "Prepare role-specific coding questions and behavioral interview scenarios."
            ]
        }

    # ==========================================
    # 3. AI Opportunity Recommendation & Match Scoring
    # ==========================================
    def calculate_match_score(self, profile_data, opportunity_dict):
        """Calculates a comprehensive multi-factor match percentage (0-100) with detailed explainability & preparation tips."""
        student_skills_raw = profile_data.get('skills', [])
        student_skills = []
        for s in student_skills_raw:
            if isinstance(s, dict):
                student_skills.append(s.get('skill_name', '').lower().strip())
            elif isinstance(s, str):
                student_skills.append(s.lower().strip())
        student_skills_set = set(filter(None, student_skills))

        req_skills_raw = opportunity_dict.get('required_skills', []) or []
        req_skills = [str(s).lower().strip() for s in req_skills_raw if str(s).strip()]
        if not req_skills:
            req_skills = ['programming', 'problem solving']

        # 1. Skill Overlap & Fuzzy Match
        matched_skill_set = set()
        for rs in req_skills:
            for ss in student_skills_set:
                if rs in ss or ss in rs or rs == ss:
                    matched_skill_set.add(rs)
                    break

        skill_overlap_ratio = len(matched_skill_set) / max(1, len(req_skills))
        skill_score = min(45, int(skill_overlap_ratio * 45))

        # 2. Career Goal & Target Role Alignment
        goal = (profile_data.get('career_goal') or profile_data.get('target_role') or '').lower()
        title = opportunity_dict.get('title', '').lower()
        opp_type = opportunity_dict.get('opportunity_type', '').lower()
        desc = opportunity_dict.get('description', '').lower()

        alignment_score = 15
        goal_words = [w for w in re.split(r'\W+', goal) if len(w) > 3]
        if any(w in title or w in desc for w in goal_words):
            alignment_score = 30
        elif any(w in title for w in ['software', 'engineer', 'developer', 'ai', 'data', 'cloud', 'intern']):
            alignment_score = 22

        # 3. Academic & Eligibility Fit
        degree = str(profile_data.get('degree') or 'B.Tech').lower()
        branch = str(profile_data.get('branch') or 'Computer Science').lower()
        grad_year = profile_data.get('graduation_year') or 2026
        cgpa = float(profile_data.get('cgpa') or 7.5)
        
        eligibility_score = 15
        if cgpa >= 8.0:
            eligibility_score += 5
        elif cgpa < 6.5:
            eligibility_score -= 3

        # 4. Experience & Projects Fit
        projects = profile_data.get('projects', [])
        certs = profile_data.get('certifications', [])
        exp_score = min(10, (len(projects) * 3) + (len(certs) * 2))

        # Total Match Calculation
        total_match = min(98, max(30, skill_score + alignment_score + eligibility_score + exp_score))

        matched_skill_names = [s.title() for s in matched_skill_set]
        missing_skill_names = [s.title() for s in (set(req_skills) - matched_skill_set)]

        # Detailed explainability reasons
        reasons = []
        if matched_skill_names:
            reasons.append(f"Strong overlap with your verified skills in {', '.join(matched_skill_names[:4])}.")
        else:
            reasons.append("Covers fundamental concepts aligned with your technical degree.")

        if alignment_score >= 25:
            target_title = profile_data.get('target_role') or profile_data.get('career_goal') or 'Software Engineering'
            reasons.append(f"High strategic alignment with your career aspiration of becoming a {target_title}.")

        if cgpa >= 7.5:
            reasons.append(f"Your academic standing ({cgpa} CGPA) satisfies the target eligibility profile.")

        mode_str = opportunity_dict.get('event_mode') or ('Remote' if opportunity_dict.get('is_remote') else 'Offline')
        if 'remote' in mode_str.lower() or 'online' in mode_str.lower():
            reasons.append("Flexible virtual / online format allows seamless balance with your college curriculum.")

        # Tailored Preparation Tips
        prep_tips = []
        if missing_skill_names:
            prep_tips.append(f"Bridge high-priority skills: Study {missing_skill_names[0]} core patterns and complete a mini-demo project.")
        if opp_type == 'hackathon':
            prep_tips.append(f"Form a cross-functional team (Frontend + Backend + AI) and formulate a clear 2-minute elevator pitch for '{opportunity_dict.get('title')}'.")
        elif opp_type in ['internship', 'job']:
            prep_tips.append(f"Tailor your AI Resume to highlight projects demonstrating {', '.join((matched_skill_names + req_skills)[:3])}.")
        elif opp_type == 'certification':
            prep_tips.append("Review official practice exam questions and schedule 5-8 focused study hours per week.")
        elif opp_type == 'competition':
            prep_tips.append("Practice time-complexity optimization on graph algorithms and dynamic programming.")
        else:
            prep_tips.append("Take structured notes and build a hands-on GitHub repository to document your learnings.")

        return {
            "match_score": total_match,
            "matched_skills": matched_skill_names,
            "missing_skills": missing_skill_names,
            "reasons": reasons,
            "preparation_tips": prep_tips,
            "dna_breakdown": {
                "skill_match": min(100, int((skill_score / 45) * 100)),
                "goal_alignment": min(100, int((alignment_score / 30) * 100)),
                "eligibility_fit": min(100, int((eligibility_score / 20) * 100)),
                "experience_fit": min(100, int((exp_score / 10) * 100))
            }
        }

    # ==========================================
    # 4. AI Career Roadmap Generation (7 Exact Stages)
    # ==========================================
    def generate_roadmap(self, profile_data, target_role):
        """
        Generates a 7-stage comprehensive personalized career roadmap.
        Stages:
        1. Current Skill Assessment
        2. Skills to Learn
        3. Projects to Build
        4. Certifications to Earn
        5. Internship Preparation
        6. Interview Preparation
        7. Placement Preparation
        """
        prompt = f"""
Generate a structured, 7-stage personalized career roadmap for a university student aiming to become a "{target_role}".
The 7 stages MUST be EXACTLY:
1. Current Skill Assessment
2. Skills to Learn
3. Projects to Build
4. Certifications to Earn
5. Internship Preparation
6. Interview Preparation
7. Placement Preparation

For every skill and milestone in the roadmap, recommend real, trusted, top-tier learning resources with valid URLs (e.g., Python Official Docs, MDN Web Docs, LeetCode, W3Schools, GitHub, AWS Skill Builder, PostgreSQL Docs, Docker Docs).

Return a JSON array of exactly 7 objects. Each object must have:
- "stage_number": integer (1 to 7)
- "stage_name": string (the exact stage name from the list above)
- "title": string (engaging, actionable milestone title)
- "description": string (clear summary of goals for this stage)
- "action_items": list of 2-4 objects [{{"id": "s1_1", "text": "Action item description", "completed": false}}]
- "resources": list of 2-4 objects [
    {{
        "title": "Platform or Resource Name (e.g., MDN Web Docs — JavaScript)",
        "url": "https://...",
        "description": "Short 1-sentence description of what to learn here",
        "type": "doc|course|practice|tool|repo",
        "action_label": "Learn Now"
    }}
]

Student Profile:
- Target Role: {target_role}
- Current Skills: {json.dumps([s.get('skill_name') for s in profile_data.get('skills', [])])}
- Degree: {profile_data.get('degree', 'B.Tech')} in {profile_data.get('branch', 'Computer Science')}
- College: {profile_data.get('college_name', 'University')}
- CGPA: {profile_data.get('cgpa', '8.0')}

Respond ONLY with valid JSON.
"""
        raw_res = self._call_gemini_raw(prompt)
        parsed = self._clean_and_parse_json(raw_res, None)
        if parsed and isinstance(parsed, list) and len(parsed) >= 6:
            stage_names = [
                "Current Skill Assessment",
                "Skills to Learn",
                "Projects to Build",
                "Certifications to Earn",
                "Internship Preparation",
                "Interview Preparation",
                "Placement Preparation"
            ]
            for i, stg in enumerate(parsed[:7]):
                stg['stage_number'] = i + 1
                stg['stage_name'] = stage_names[i]
                for r in stg.get('resources', []):
                    if not r.get('action_label'):
                        r['action_label'] = 'Visit Resource'
            return parsed[:7]

        # Fallback 7-Stage Roadmap tailored to role
        return self._fallback_roadmap(profile_data, target_role)

    def _fallback_roadmap(self, profile_data, target_role):
        role = (target_role or "Full-Stack Software Engineer").strip()
        role_lower = role.lower()
        user_skills = [s.get('skill_name') for s in profile_data.get('skills', []) if s.get('skill_name')]
        skills_str = ", ".join(user_skills[:3]) if user_skills else "Python/JavaScript"

        # Determine Role-Specific Learning Resources & Skills
        if any(k in role_lower for k in ['ai', 'machine learning', 'data science', 'data analyst']):
            stage2_title = "Data Science, Deep Learning & Python AI Libraries"
            stage2_desc = "Master Python data science stack (NumPy, Pandas), machine learning algorithms (Scikit-Learn), and modern neural networks (PyTorch/TensorFlow)."
            stage2_actions = [
                {"id": "s2_1", "text": "Master Python data analysis libraries: Pandas, NumPy, and Matplotlib.", "completed": False},
                {"id": "s2_2", "text": "Learn foundational machine learning: Regression, Classification, Clustering, and Evaluation metrics.", "completed": False},
                {"id": "s2_3", "text": "Implement deep learning models (CNNs/Transformers) using PyTorch.", "completed": False}
            ]
            stage2_resources = [
                {"title": "Python Official Documentation", "url": "https://docs.python.org/3/tutorial/", "description": "Master core Python syntax, OOP, and data structures.", "type": "doc", "action_label": "Learn Now"},
                {"title": "Kaggle Learn Data Science & ML", "url": "https://www.kaggle.com/learn", "description": "Hands-on interactive courses in Python, Pandas, Machine Learning, and SQL.", "type": "practice", "action_label": "Start Learning"},
                {"title": "PyTorch Official Tutorials", "url": "https://pytorch.org/tutorials/", "description": "Deep learning models, tensors, and neural network training pipelines.", "type": "doc", "action_label": "Visit Resource"},
                {"title": "Scikit-Learn Machine Learning Guide", "url": "https://scikit-learn.org/stable/user_guide.html", "description": "Algorithms, data preprocessing, and model evaluation.", "type": "doc", "action_label": "Learn Now"}
            ]
            stage3_title = "Flagship AI / ML Capstone & Live Pipeline Deployment"
            stage3_desc = "Train, validate, and deploy an end-to-end ML model API with Streamlit/FastAPI and cloud hosting."
            stage3_resources = [
                {"title": "FastAPI ML Model Serving Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/", "description": "Build high-performance REST APIs for ML model inferences.", "type": "doc", "action_label": "Visit Resource"},
                {"title": "Hugging Face Models & Transformers", "url": "https://huggingface.co/docs", "description": "Integrate open-source LLMs, embeddings, and NLP pipelines.", "type": "repo", "action_label": "Explore Platform"},
                {"title": "GitHub Skills & Actions CI/CD", "url": "https://skills.github.com", "description": "Automated data workflows, model evaluation testing, and version control.", "type": "tool", "action_label": "Learn Now"}
            ]
            stage4_resources = [
                {"title": "AWS Certified Machine Learning - Specialty", "url": "https://aws.amazon.com/certification/certified-machine-learning-specialty/", "description": "Industry benchmark for cloud ML architectures.", "type": "course", "action_label": "Explore Certification"},
                {"title": "Google Cloud Professional Data Engineer", "url": "https://cloud.google.com/learn/certification/data-engineer", "description": "Data processing and ML deployment credential.", "type": "course", "action_label": "Visit Resource"}
            ]
        elif any(k in role_lower for k in ['cloud', 'devops', 'infrastructure', 'sre']):
            stage2_title = "Cloud Infrastructure, Containerization & CI/CD Pipelines"
            stage2_desc = "Master Linux system administration, Docker containers, Kubernetes cluster orchestration, and automated pipelines."
            stage2_actions = [
                {"id": "s2_1", "text": "Master Linux CLI commands, Bash scripting, and networking fundamentals.", "completed": False},
                {"id": "s2_2", "text": "Containerize microservices with Docker and multi-stage Dockerfiles.", "completed": False},
                {"id": "s2_3", "text": "Learn Infrastructure as Code (IaC) using Terraform.", "completed": False}
            ]
            stage2_resources = [
                {"title": "Linux Journey — System Administration", "url": "https://linuxjourney.com", "description": "Learn Linux commands, networking, permissions, and process management.", "type": "course", "action_label": "Learn Now"},
                {"title": "Docker Official Documentation", "url": "https://docs.docker.com/get-started/", "description": "Build container images, compose files, and containerized architectures.", "type": "doc", "action_label": "Visit Resource"},
                {"title": "Kubernetes Official Tutorials", "url": "https://kubernetes.io/docs/tutorials/", "description": "Deploy, scale, and manage containerized clusters.", "type": "doc", "action_label": "Learn Now"},
                {"title": "HashiCorp Terraform Tutorials", "url": "https://developer.hashicorp.com/terraform/tutorials", "description": "Provision reproducible cloud infrastructure via code.", "type": "doc", "action_label": "Start Learning"}
            ]
            stage3_title = "Automated Cloud CI/CD & Multi-Region Kubernetes Project"
            stage3_desc = "Engineer an automated GitOps deployment pipeline deploying high-availability services to AWS/GCP."
            stage3_resources = [
                {"title": "GitHub Actions Official Guide", "url": "https://docs.github.com/en/actions", "description": "Automate build, test, linting, and cloud deployments on git push.", "type": "doc", "action_label": "Learn Now"},
                {"title": "AWS Skill Builder Free DevOps Track", "url": "https://explore.skillbuilder.aws", "description": "Official AWS training for EC2, S3, IAM, ECS, and CloudWatch.", "type": "course", "action_label": "Visit Resource"}
            ]
            stage4_resources = [
                {"title": "AWS Certified Solutions Architect Associate", "url": "https://aws.amazon.com/certification/certified-solutions-architect-associate/", "description": "Premier global cloud credential for systems design.", "type": "course", "action_label": "Explore Exam"},
                {"title": "CKA: Certified Kubernetes Administrator", "url": "https://www.cncf.io/certification/cka/", "description": "Hands-on performance-based Kubernetes certification.", "type": "course", "action_label": "Learn Now"}
            ]
        elif any(k in role_lower for k in ['cyber', 'security']):
            stage2_title = "Network Security, Cryptography & Threat Analysis"
            stage2_desc = "Master web application security (OWASP Top 10), penetration testing fundamentals, and secure coding practices."
            stage2_actions = [
                {"id": "s2_1", "text": "Master TCP/IP networking, subnetting, and packet analysis via Wireshark.", "completed": False},
                {"id": "s2_2", "text": "Learn OWASP Top 10 vulnerabilities (SQLi, XSS, CSRF, IDOR) and remediation.", "completed": False},
                {"id": "s2_3", "text": "Understand cryptographic algorithms, SSL/TLS certificates, and hashing mechanisms.", "completed": False}
            ]
            stage2_resources = [
                {"title": "OWASP Top 10 Web Security", "url": "https://owasp.org/www-project-top-ten/", "description": "Gold standard web vulnerability classification and defense guide.", "type": "doc", "action_label": "Learn Now"},
                {"title": "TryHackMe — Cybersecurity Training", "url": "https://tryhackme.com", "description": "Hands-on guided cybersecurity labs from beginner to advanced.", "type": "practice", "action_label": "Start Practice"},
                {"title": "OverTheWire Security Wargames", "url": "https://overthewire.org/wargames/", "description": "Interactive CLI security games to master Linux security concepts.", "type": "practice", "action_label": "Play Labs"}
            ]
            stage3_title = "Vulnerability Assessment & Automated Security Scanner Capstone"
            stage3_desc = "Build a automated security audit tool and conduct penetration tests in safe virtual labs."
            stage3_resources = [
                {"title": "PortSwigger Web Security Academy", "url": "https://portswigger.net/web-security", "description": "Free online web security training from the creators of Burp Suite.", "type": "practice", "action_label": "Learn Now"},
                {"title": "Wireshark Official User Guide", "url": "https://www.wireshark.org/docs/", "description": "Deep-dive network packet sniffing and traffic analysis.", "type": "doc", "action_label": "Visit Resource"}
            ]
            stage4_resources = [
                {"title": "CompTIA Security+ Certification", "url": "https://www.comptia.org/certifications/security", "description": "Entry-level benchmark credential for IT security roles.", "type": "course", "action_label": "Explore Exam"},
                {"title": "Certified Ethical Hacker (CEH)", "url": "https://www.eccouncil.org/train-certify/certified-ethical-hacker-ceh/", "description": "Recognized ethical hacking and penetration testing certification.", "type": "course", "action_label": "Visit Resource"}
            ]
        else:
            # Default Full-Stack / Software Engineering Track
            stage2_title = "Modern Full-Stack Engineering, Frameworks & Database Mastery"
            stage2_desc = "Master modern responsive frontend (React / HTML / CSS / JavaScript), production backend architectures (Python / Node.js / APIs), and SQL databases."
            stage2_actions = [
                {"id": "s2_1", "text": "Master JavaScript (ES6+), modern DOM manipulation, and asynchronous programming (Promises / async-await).", "completed": False},
                {"id": "s2_2", "text": "Build modular Single Page Applications with React and modern state management.", "completed": False},
                {"id": "s2_3", "text": "Design scalable RESTful APIs with Python (FastAPI/Flask) or Node.js.", "completed": False},
                {"id": "s2_4", "text": "Master SQL query optimization, indexes, and migrations with PostgreSQL / MySQL.", "completed": False}
            ]
            stage2_resources = [
                {"title": "MDN Web Docs — HTML, CSS & JavaScript", "url": "https://developer.mozilla.org/", "description": "The authoritative industry reference for HTML, CSS, and modern JavaScript syntax.", "type": "doc", "action_label": "Learn Now"},
                {"title": "Python Official Documentation", "url": "https://www.python.org/", "description": "Core Python language tutorial, data structures, and standard library.", "type": "doc", "action_label": "Learn Now"},
                {"title": "W3Schools SQL & Database Tutorial", "url": "https://www.w3schools.com/sql/", "description": "Relational schema design, queries, indexes, joins, and database operations.", "type": "doc", "action_label": "Learn Now"},
                {"title": "React Official Documentation", "url": "https://react.dev/learn", "description": "Interactive documentation for React components, hooks, and best practices.", "type": "doc", "action_label": "Learn Now"}
            ]
            stage3_title = "Flagship Full-Stack Capstone & Cloud Deployment"
            stage3_desc = "Engineer an end-to-end production web platform featuring authentication, real-time updates, Docker containerization, and automated CI/CD."
            stage3_resources = [
                {"title": "Docker Official Getting Started Guide", "url": "https://docs.docker.com/get-started/", "description": "Containerize full-stack services and write clean Docker compose configs.", "type": "doc", "action_label": "Visit Resource"},
                {"title": "GitHub Skills — Git & Workflows", "url": "https://skills.github.com/", "description": "Interactive GitHub tutorials for branching, pull requests, and automated actions.", "type": "tool", "action_label": "Learn Now"},
                {"title": "Codecrafters — Build Your Own Systems", "url": "https://github.com/codecrafters-io/build-your-own-x", "description": "Recreate complex systems (databases, Git, HTTP servers) from scratch.", "type": "repo", "action_label": "Visit Resource"}
            ]
            stage4_resources = [
                {"title": "AWS Cloud Training & Certification", "url": "https://aws.amazon.com/training/", "description": "Official AWS training covering compute, storage, databases, and architectures.", "type": "course", "action_label": "Visit Resource"},
                {"title": "Meta Full-Stack Professional Certificate", "url": "https://www.coursera.org/professional-certificates/meta-front-end-developer", "description": "Accredited career certificate validating full-stack engineering competency.", "type": "course", "action_label": "Visit Resource"}
            ]

        stages = [
            {
                "stage_number": 1,
                "stage_name": "Current Skill Assessment",
                "title": f"Baseline Technical Audit & Gap Analysis for {role}",
                "description": f"Benchmark your foundational programming competencies, data structures, and problem-solving readiness against modern {role} job requirements.",
                "action_items": [
                    {"id": "s1_1", "text": f"Complete a timed baseline assessment on core DSA ({skills_str}) and problem solving.", "completed": True},
                    {"id": "s1_2", "text": "Audit existing GitHub repositories for clean READMEs, documentation, and commit hygiene.", "completed": False},
                    {"id": "s1_3", "text": f"Document current skill gaps against Tier-1 {role} job descriptions.", "completed": False}
                ],
                "resources": [
                    {"title": "LeetCode Problem Solving & Study Plan", "url": "https://leetcode.com/", "description": "Essential coding questions categorized by core data structure and algorithm patterns.", "type": "practice", "action_label": "Start Practice"},
                    {"title": "Roadmap.sh Interactive Developer Guides", "url": "https://roadmap.sh", "description": "Community-driven visual roadmaps and skill checklists for all tech domains.", "type": "doc", "action_label": "Visit Resource"},
                    {"title": "HackerRank Algorithms & Problem Solving", "url": "https://www.hackerrank.com/domains/algorithms", "description": "Practice algorithms and data structures with automatic test runner.", "type": "practice", "action_label": "Learn Now"}
                ]
            },
            {
                "stage_number": 2,
                "stage_name": "Skills to Learn",
                "title": stage2_title,
                "description": stage2_desc,
                "action_items": stage2_actions,
                "resources": stage2_resources
            },
            {
                "stage_number": 3,
                "stage_name": "Projects to Build",
                "title": stage3_title,
                "description": stage3_desc,
                "action_items": [
                    {"id": "s3_1", "text": f"Build a flagship {role} capstone application featuring real-time data and database caching.", "completed": False},
                    {"id": "s3_2", "text": "Implement comprehensive unit and integration tests with >80% test coverage.", "completed": False},
                    {"id": "s3_3", "text": "Deploy to cloud (AWS / Vercel / Render) with Docker containerization and automated CI/CD.", "completed": False}
                ],
                "resources": stage3_resources
            },
            {
                "stage_number": 4,
                "stage_name": "Certifications to Earn",
                "title": "Industry-Recognized Credential Validation",
                "description": "Validate your skills and enhance your resume visibility with accredited cloud and vendor certifications.",
                "action_items": [
                    {"id": "s4_1", "text": "Enroll in and complete a relevant cloud/developer certification.", "completed": False},
                    {"id": "s4_2", "text": "Publish credential badges on LinkedIn and attach verified certificate IDs to your resume.", "completed": False}
                ],
                "resources": stage4_resources
            },
            {
                "stage_number": 5,
                "stage_name": "Internship Preparation",
                "title": "Application Strategy & Targeted Outreach",
                "description": "Target high-growth startups and tech leaders with customized resumes, portfolio links, and warm referrals.",
                "action_items": [
                    {"id": "s5_1", "text": "Tailor resume bullets using action verbs and quantified metrics via Career DNA AI Builder.", "completed": False},
                    {"id": "s5_2", "text": "Set up alerts and apply to 15+ target opportunities via Career DNA AI tracker.", "completed": False},
                    {"id": "s5_3", "text": "Connect with 10 alumni and industry engineers on LinkedIn for warm referrals.", "completed": False}
                ],
                "resources": [
                    {"title": "LinkedIn Student Career & Networking Guide", "url": "https://www.linkedin.com/help/linkedin/answer/a548441", "description": "Master LinkedIn profile optimization, connection requests, and recruiter outreach.", "type": "doc", "action_label": "Learn Now"},
                    {"title": "GitHub Student Developer Pack", "url": "https://education.github.com/pack", "description": "Free cloud hosting, domains, and developer tools for enrolled students.", "type": "tool", "action_label": "Claim Free Pack"}
                ]
            },
            {
                "stage_number": 6,
                "stage_name": "Interview Preparation",
                "title": "Technical Coding & Behavioral STAR Drills",
                "description": "Master live coding patterns, system design fundamentals, and structured STAR responses for behavioral rounds.",
                "action_items": [
                    {"id": "s6_1", "text": "Solve 75+ medium LeetCode problems (Array, Tree, Graph, DP, Two Pointers).", "completed": False},
                    {"id": "s6_2", "text": "Conduct 3 peer mock technical interviews on Pramp / Interviewing.io.", "completed": False},
                    {"id": "s6_3", "text": "Draft STAR method responses for top 10 behavioral questions (leadership, conflict, failure).", "completed": False}
                ],
                "resources": [
                    {"title": "Tech Interview Handbook", "url": "https://www.techinterviewhandbook.org", "description": "Curated interview preparation guide covering behavioral, resume, and coding rounds.", "type": "doc", "action_label": "Visit Guide"},
                    {"title": "System Design Primer by Donne Martin", "url": "https://github.com/donnemartin/system-design-primer", "description": "Learn how to design large-scale, fault-tolerant distributed systems.", "type": "repo", "action_label": "Study Primer"},
                    {"title": "NeetCode 150 Coding Practice", "url": "https://neetcode.io/practice", "description": "Video solutions and code walkthroughs for all top interview patterns.", "type": "practice", "action_label": "Start Practice"}
                ]
            },
            {
                "stage_number": 7,
                "stage_name": "Placement Preparation",
                "title": "Offer Evaluation, Compensation & Day-1 Success",
                "description": "Evaluate full-time compensation structures, negotiate offers professionally, and master git branching for team onboarding.",
                "action_items": [
                    {"id": "s7_1", "text": "Review offer letters, stipend structures, and benefits packages.", "completed": False},
                    {"id": "s7_2", "text": "Learn team codebase navigation and Git branching workflows for day 1 readiness.", "completed": False}
                ],
                "resources": [
                    {"title": "Levels.fyi Tech Compensation & Salary Guide", "url": "https://www.levels.fyi", "description": "Research verified software engineer salaries, levels, and negotiation benchmarks.", "type": "tool", "action_label": "Explore Salaries"},
                    {"title": "Interviewing.io Technical Mock Rounds", "url": "https://interviewing.io", "description": "Practice realistic technical rounds with senior FAANG hiring managers.", "type": "practice", "action_label": "Visit Platform"}
                ]
            }
        ]
        return stages
        return stages

    # ==========================================
    # 5. AI Resume Bullet & Section Enhancement
    # ==========================================
    def improve_resume_section(self, section_type, text_content, context=None):
        """
        Enhances resume text using strong action verbs, quantifiable metrics,
        and high ATS keyword density.
        """
        prompt = f"""
You are a senior tech recruiter and resume specialist. Rewrite and elevate this {section_type} for a student tech resume.
Requirements:
1. Start bullets with dynamic action verbs (e.g., Engineered, Architected, Accelerated, Reduced).
2. Incorporate quantified impact / metrics (e.g., 'boosting throughput by 35%', 'cutting latency by 200ms').
3. Keep concise, professional, and ATS-optimized.

Original text:
{text_content}

Context:
{json.dumps(context or {})}

Return a JSON object with:
- "improved_text": "The elevated text / bullet points"
- "key_improvements": ["List of 2-3 specific improvements made"],
- "ats_keywords_added": ["List of relevant tech keywords included"]
"""
        raw_res = self._call_gemini_raw(prompt)
        parsed = self._clean_and_parse_json(raw_res, None)
        if parsed and isinstance(parsed, dict) and 'improved_text' in parsed:
            return parsed

        # Algorithmic fallback
        cleaned = text_content.strip()
        if section_type == 'career_objective':
            improved = "Results-driven software engineering student specializing in scalable distributed architectures and modern full-stack development. Proven track record in engineering high-performance web applications, optimizing relational databases, and collaborating across Agile sprints to deliver reliable digital products."
            keywords = ["Distributed Systems", "Full-Stack Development", "Agile Sprints", "Database Optimization"]
        elif section_type == 'project':
            improved = "• Architected and deployed an end-to-end full-stack web platform using modern frameworks, handling 500+ concurrent requests with 99.9% uptime.\n• Implemented secure JWT authentication and optimized relational queries, reducing average API response latency by 42%.\n• Containerized application microservices with Docker and integrated automated CI/CD pipelines via GitHub Actions."
            keywords = ["Docker", "CI/CD", "JWT Authentication", "Query Optimization", "High Availability"]
        else:
            improved = "• Spearheaded feature development across cross-functional sprints, accelerating product delivery timelines by 25%.\n• Designed and maintained robust RESTful endpoints with comprehensive error handling and automated unit test suites."
            keywords = ["Cross-functional Collaboration", "RESTful APIs", "Unit Testing", "Sprint Velocity"]

        return {
            "improved_text": improved,
            "key_improvements": [
                "Transformed passive phrasing into impactful action verbs.",
                "Added measurable outcomes and system performance indicators.",
                "Reinforced industry-standard tech stack terminology."
            ],
            "ats_keywords_added": keywords
        }

    # ==========================================
    # 6. AI Resume ATS Scoring & Keyword Diagnostic
    # ==========================================
    def score_resume_ats(self, resume_data, target_role="Software Engineer"):
        """Evaluates resume ATS compliance, keyword saturation, and formatting score."""
        prompt = f"""
Evaluate this student's resume for ATS (Applicant Tracking System) friendliness for the target role of "{target_role}".
Return a JSON object with:
- "ats_score": integer from 0 to 100
- "formatting_score": integer from 0 to 100
- "keyword_density_score": integer from 0 to 100
- "strengths": list of 3 strings
- "identified_relevant_skills": list of 4-6 technical skills detected in the resume that match {target_role}
- "missing_keywords": list of 3-5 crucial keywords missing for {target_role}
- "actionable_suggestions": list of 3-4 specific revisions to achieve 90+ ATS score.

Resume Content:
{json.dumps(resume_data)}
"""
        raw_res = self._call_gemini_raw(prompt)
        parsed = self._clean_and_parse_json(raw_res, None)
        if parsed and isinstance(parsed, dict) and 'ats_score' in parsed:
            if 'identified_relevant_skills' not in parsed:
                parsed['identified_relevant_skills'] = ["Python", "SQL", "Git", "REST APIs"]
            return parsed

        # Heuristic ATS scorer
        text_corpus = str(resume_data).lower()
        score = 65
        missing_kw = []
        identified_skills = []

        target_keywords = {
            'software': ['git', 'agile', 'rest apis', 'docker', 'unit testing', 'sql', 'algorithms', 'python', 'javascript'],
            'data': ['python', 'pandas', 'sql', 'scikit-learn', 'data pipeline', 'tableau', 'statistics', 'machine learning'],
            'web': ['javascript', 'typescript', 'react', 'css3', 'responsive design', 'web security', 'html5', 'node.js']
        }

        role_key = 'software'
        if 'data' in target_role.lower() or 'ai' in target_role.lower(): role_key = 'data'
        elif 'web' in target_role.lower() or 'front' in target_role.lower(): role_key = 'web'

        found_count = 0
        for kw in target_keywords[role_key]:
            if kw in text_corpus:
                found_count += 1
                identified_skills.append(kw.title())
            else:
                missing_kw.append(kw.title())

        score += (found_count * 4)
        if len(text_corpus) > 300: score += 5
        score = min(95, max(50, score))

        if not identified_skills:
            identified_skills = ["Programming Fundamentals", "Git Version Control", "Data Structures"]

        return {
            "ats_score": score,
            "formatting_score": 88,
            "keyword_density_score": min(95, max(45, found_count * 12)),
            "strengths": [
                "Clean structural hierarchy suitable for ATS text parsing scanners.",
                "Well-defined project summaries and academic credentials.",
                "Technical skill categorization is clear."
            ],
            "identified_relevant_skills": identified_skills[:6],
            "missing_keywords": missing_kw[:5] if missing_kw else ["Microservices", "Cloud Deployment (AWS/GCP)", "Automated Testing"],
            "actionable_suggestions": [
                f"Incorporate missing target keywords: {', '.join(missing_kw[:3]) if missing_kw else 'Docker, CI/CD, Unit Testing'}.",
                "Ensure every project bullet begins with an action verb and includes quantified metrics (% speedup, user count).",
                "Maintain clean standard typography and avoid complex tables or multi-column graphical shapes."
            ],
            "target_role": target_role
        }


# Singleton instance
gemini_service = GeminiService()
