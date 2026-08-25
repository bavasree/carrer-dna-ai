from datetime import datetime
import json
from . import db

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id', ondelete='SET NULL'), nullable=True)
    company_name = db.Column(db.String(150), nullable=False)
    position_title = db.Column(db.String(150), nullable=False)
    opportunity_type = db.Column(db.String(50), default='job')  # internship, hackathon, certification, course, competition, job
    status = db.Column(db.String(30), default='applied', index=True)  # type-aware status
    applied_date = db.Column(db.Date, default=datetime.utcnow().date)
    interview_date = db.Column(db.DateTime, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    salary_offered = db.Column(db.String(100), nullable=True)
    submitted_details_json = db.Column(db.Text, nullable=True)  # Full JSON object with form fields
    resume_filename = db.Column(db.String(255), nullable=True)  # Uploaded file or AI resume flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def submitted_details(self):
        if not self.submitted_details_json:
            return {}
        try:
            return json.loads(self.submitted_details_json)
        except Exception:
            return {}

    @submitted_details.setter
    def submitted_details(self, value):
        self.submitted_details_json = json.dumps(value if isinstance(value, dict) else {})

    def to_dict(self):
        details = self.submitted_details
        resume_url = None
        if self.resume_filename:
            if self.resume_filename.startswith('http'):
                resume_url = self.resume_filename
            else:
                resume_url = f'/api/applications/{self.id}/resume'

        return {
            'id': self.id,
            'student_id': self.student_id,
            'opportunity_id': self.opportunity_id,
            'company_name': self.company_name,
            'position_title': self.position_title,
            'opportunity_type': self.opportunity_type,
            'status': self.status,
            'applied_date': self.applied_date.strftime('%Y-%m-%d') if self.applied_date else None,
            'interview_date': self.interview_date.strftime('%Y-%m-%d %H:%M') if self.interview_date else None,
            'deadline': self.deadline.strftime('%Y-%m-%d') if self.deadline else None,
            'notes': self.notes,
            'salary_offered': self.salary_offered,
            'submitted_details': details,
            'resume_filename': self.resume_filename,
            'resume_url': resume_url,
            'has_resume': bool(self.resume_filename),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<Application {self.position_title} at {self.company_name} ({self.status})>'
