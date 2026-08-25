from datetime import datetime
import json
from . import db

class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), default='My Professional Resume')
    template_name = db.Column(db.String(50), default='modern')  # 'modern', 'classic'
    career_objective = db.Column(db.Text, nullable=True)
    skills_summary = db.Column(db.Text, nullable=True)
    ats_score = db.Column(db.Integer, default=70)  # 0 to 100
    ats_feedback_json = db.Column(db.Text, nullable=True)  # JSON
    content_data_json = db.Column(db.Text, nullable=True)  # JSON snapshot of full sections
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def ats_feedback(self):
        if not self.ats_feedback_json:
            return {}
        try:
            return json.loads(self.ats_feedback_json)
        except Exception:
            return {}

    @ats_feedback.setter
    def ats_feedback(self, value):
        self.ats_feedback_json = json.dumps(value if isinstance(value, dict) else {})

    @property
    def content_data(self):
        if not self.content_data_json:
            return {}
        try:
            return json.loads(self.content_data_json)
        except Exception:
            return {}

    @content_data.setter
    def content_data(self, value):
        self.content_data_json = json.dumps(value if isinstance(value, dict) else {})

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'template_name': self.template_name,
            'career_objective': self.career_objective,
            'skills_summary': self.skills_summary,
            'ats_score': self.ats_score,
            'ats_feedback': self.ats_feedback,
            'content_data': self.content_data,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

    def __repr__(self):
        return f'<Resume {self.title} (Student:{self.student_id})>'
