from datetime import datetime
import json
from . import db

class OpportunityCategory(db.Model):
    __tablename__ = 'opportunity_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    icon = db.Column(db.String(50), default='briefcase')
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    opportunities = db.relationship('Opportunity', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'icon': self.icon,
            'description': self.description,
            'opportunity_count': self.opportunities.count()
        }


class Opportunity(db.Model):
    __tablename__ = 'opportunities'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('opportunity_categories.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    company_name = db.Column(db.String(200), nullable=False)
    opportunity_type = db.Column(db.String(50), nullable=False, index=True)  # internship, hackathon, certification, course, competition, job
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150), default='Remote')
    is_remote = db.Column(db.Boolean, default=True)
    stipend_salary = db.Column(db.String(100), nullable=True)  # e.g., "$1500/month", "Free", "$80,000/year", "Prizes: $10,000"
    deadline = db.Column(db.DateTime, nullable=True)
    apply_url = db.Column(db.String(500), nullable=False)
    required_skills_json = db.Column(db.Text, nullable=True)  # JSON serialized list of skills
    eligibility_criteria = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active', index=True)  # active, closed, draft
    experience_level = db.Column(db.String(50), default='Any')  # Beginner, Intermediate, Advanced, All Levels
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    saved_by_students = db.relationship('SavedOpportunity', backref='opportunity', cascade='all, delete-orphan', lazy='dynamic')
    applications = db.relationship('Application', backref='opportunity', lazy='dynamic')

    @property
    def required_skills(self):
        if not self.required_skills_json:
            return []
        try:
            return json.loads(self.required_skills_json)
        except Exception:
            return [s.strip() for s in self.required_skills_json.split(',') if s.strip()]

    @required_skills.setter
    def required_skills(self, value):
        if isinstance(value, list):
            self.required_skills_json = json.dumps(value)
        elif isinstance(value, str):
            self.required_skills_json = json.dumps([s.strip() for s in value.split(',') if s.strip()])
        else:
            self.required_skills_json = json.dumps([])

    def to_dict(self, student_id=None):
        is_saved = False
        is_applied = False
        application_status = None
        application_id = None

        if student_id:
            is_saved = SavedOpportunity.query.filter_by(student_id=student_id, opportunity_id=self.id).first() is not None
            applied_entry = self.applications.filter_by(student_id=student_id).first()
            if applied_entry:
                is_applied = True
                application_status = applied_entry.status
                application_id = applied_entry.id

        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'General',
            'title': self.title,
            'company_name': self.company_name,
            'opportunity_type': self.opportunity_type,
            'description': self.description,
            'location': self.location,
            'is_remote': self.is_remote,
            'stipend_salary': self.stipend_salary,
            'deadline': self.deadline.strftime('%Y-%m-%d') if self.deadline else None,
            'apply_url': self.apply_url,
            'required_skills': self.required_skills,
            'eligibility_criteria': self.eligibility_criteria,
            'status': self.status,
            'experience_level': self.experience_level,
            'is_saved': is_saved,
            'is_applied': is_applied,
            'application_status': application_status,
            'application_id': application_id,
            'applicants_count': self.applications.count(),
            'posted_at': self.posted_at.strftime('%Y-%m-%d') if self.posted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Opportunity {self.title} ({self.opportunity_type})>'


class SavedOpportunity(db.Model):
    __tablename__ = 'saved_opportunities'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id', ondelete='CASCADE'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('student_id', 'opportunity_id', name='_student_opportunity_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'opportunity_id': self.opportunity_id,
            'opportunity': self.opportunity.to_dict(student_id=self.student_id) if self.opportunity else None,
            'saved_at': self.saved_at.isoformat() if self.saved_at else None
        }
