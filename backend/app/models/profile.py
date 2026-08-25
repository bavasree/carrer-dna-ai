from datetime import datetime
from . import db

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default='general')  # programming, framework, database, tool, cloud, data_ai, soft_skill
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category
        }


class StudentSkill(db.Model):
    __tablename__ = 'student_skills'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='SET NULL'), nullable=True)
    skill_name = db.Column(db.String(100), nullable=False)
    proficiency_level = db.Column(db.String(20), nullable=False, default='intermediate')  # beginner, intermediate, advanced, expert
    years_of_experience = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'skill_id': self.skill_id,
            'skill_name': self.skill_name,
            'proficiency_level': self.proficiency_level,
            'years_of_experience': self.years_of_experience
        }


class StudentProject(db.Model):
    __tablename__ = 'student_projects'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_stack = db.Column(db.String(255), nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    live_url = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'tech_stack': self.tech_stack,
            'github_url': self.github_url,
            'live_url': self.live_url,
            'role': self.role
        }


class StudentCertification(db.Model):
    __tablename__ = 'student_certifications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    issuing_organization = db.Column(db.String(150), nullable=False)
    issue_date = db.Column(db.String(50), nullable=True)
    credential_id = db.Column(db.String(150), nullable=True)
    credential_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'issuing_organization': self.issuing_organization,
            'issue_date': self.issue_date,
            'credential_id': self.credential_id,
            'credential_url': self.credential_url
        }


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    full_name = db.Column(db.String(150), nullable=False)
    headline = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    college_name = db.Column(db.String(200), nullable=True)
    degree = db.Column(db.String(100), nullable=True)
    branch = db.Column(db.String(100), nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    career_goal = db.Column(db.String(255), nullable=True)
    target_role = db.Column(db.String(150), nullable=True)
    interests = db.Column(db.Text, nullable=True)  # Comma separated or JSON string
    profile_completion_pct = db.Column(db.Integer, default=0)
    github_url = db.Column(db.String(255), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)
    portfolio_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skills = db.relationship('StudentSkill', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    projects = db.relationship('StudentProject', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    certifications = db.relationship('StudentCertification', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    career_analyses = db.relationship('CareerAnalysis', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    roadmaps = db.relationship('CareerRoadmap', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    resumes = db.relationship('Resume', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    applications = db.relationship('Application', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    saved_opportunities = db.relationship('SavedOpportunity', backref='student', cascade='all, delete-orphan', lazy='dynamic')

    def calculate_completion_pct(self):
        """Calculates profile completion percentage based on field weights."""
        score = 0
        total_weight = 100

        # Basic Info (25%)
        if self.full_name: score += 10
        if self.phone: score += 5
        if self.headline: score += 5
        if self.bio: score += 5

        # Academic Details (25%)
        if self.college_name: score += 5
        if self.degree: score += 5
        if self.branch: score += 5
        if self.graduation_year: score += 5
        if self.cgpa: score += 5

        # Career Direction (15%)
        if self.career_goal: score += 8
        if self.target_role: score += 7

        # Skills (15%)
        if self.skills.count() > 0:
            skill_cnt = self.skills.count()
            score += min(15, skill_cnt * 3)

        # Projects (10%)
        if self.projects.count() > 0: score += 10

        # Links & Certs (10%)
        if self.github_url or self.linkedin_url: score += 5
        if self.certifications.count() > 0: score += 5

        self.profile_completion_pct = min(100, score)
        return self.profile_completion_pct

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'headline': self.headline,
            'phone': self.phone,
            'college_name': self.college_name,
            'degree': self.degree,
            'branch': self.branch,
            'graduation_year': self.graduation_year,
            'cgpa': self.cgpa,
            'bio': self.bio,
            'career_goal': self.career_goal,
            'target_role': self.target_role,
            'interests': [i.strip() for i in self.interests.split(',')] if self.interests else [],
            'interests_raw': self.interests or '',
            'profile_completion_pct': self.profile_completion_pct,
            'github_url': self.github_url,
            'linkedin_url': self.linkedin_url,
            'portfolio_url': self.portfolio_url,
            'skills': [s.to_dict() for s in self.skills.all()],
            'projects': [p.to_dict() for p in self.projects.all()],
            'certifications': [c.to_dict() for c in self.certifications.all()],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<StudentProfile {self.full_name}>'
