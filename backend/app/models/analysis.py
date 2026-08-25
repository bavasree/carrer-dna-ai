from datetime import datetime
import json
from . import db

class CareerAnalysis(db.Model):
    __tablename__ = 'career_analyses'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    readiness_score = db.Column(db.Integer, nullable=False, default=50)  # 0 to 100
    strengths_json = db.Column(db.Text, nullable=True)
    weaknesses_json = db.Column(db.Text, nullable=True)
    skill_gaps_json = db.Column(db.Text, nullable=True)
    recommended_roles_json = db.Column(db.Text, nullable=True)
    recommended_certifications_json = db.Column(db.Text, nullable=True)
    recommended_technologies_json = db.Column(db.Text, nullable=True)
    ai_summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def _parse_json_field(self, field_val, default=None):
        if default is None:
            default = []
        if not field_val:
            return default
        try:
            return json.loads(field_val)
        except Exception:
            return default

    @property
    def strengths(self):
        return self._parse_json_field(self.strengths_json, [])

    @strengths.setter
    def strengths(self, val):
        self.strengths_json = json.dumps(val if isinstance(val, list) else [val])

    @property
    def weaknesses(self):
        return self._parse_json_field(self.weaknesses_json, [])

    @weaknesses.setter
    def weaknesses(self, val):
        self.weaknesses_json = json.dumps(val if isinstance(val, list) else [val])

    @property
    def skill_gaps(self):
        return self._parse_json_field(self.skill_gaps_json, [])

    @skill_gaps.setter
    def skill_gaps(self, val):
        self.skill_gaps_json = json.dumps(val if isinstance(val, list) else [val])

    @property
    def recommended_roles(self):
        return self._parse_json_field(self.recommended_roles_json, [])

    @recommended_roles.setter
    def recommended_roles(self, val):
        self.recommended_roles_json = json.dumps(val if isinstance(val, list) else [val])

    @property
    def recommended_certifications(self):
        return self._parse_json_field(self.recommended_certifications_json, [])

    @recommended_certifications.setter
    def recommended_certifications(self, val):
        self.recommended_certifications_json = json.dumps(val if isinstance(val, list) else [val])

    @property
    def recommended_technologies(self):
        return self._parse_json_field(self.recommended_technologies_json, [])

    @recommended_technologies.setter
    def recommended_technologies(self, val):
        self.recommended_technologies_json = json.dumps(val if isinstance(val, list) else [val])

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'readiness_score': self.readiness_score,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'skill_gaps': self.skill_gaps,
            'recommended_roles': self.recommended_roles,
            'recommended_certifications': self.recommended_certifications,
            'recommended_technologies': self.recommended_technologies,
            'ai_summary': self.ai_summary,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<CareerAnalysis Student:{self.student_id} Score:{self.readiness_score}>'
