from datetime import datetime
import json
from . import db

class CareerRoadmap(db.Model):
    __tablename__ = 'career_roadmaps'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    target_role = db.Column(db.String(150), nullable=False)
    overall_progress = db.Column(db.Integer, default=0)  # 0 to 100%
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    milestones = db.relationship('RoadmapMilestone', backref='roadmap', cascade='all, delete-orphan', order_by='RoadmapMilestone.stage_number', lazy='dynamic')

    def calculate_progress(self):
        milestones = self.milestones.all()
        total = len(milestones)
        if total == 0:
            self.overall_progress = 0
            return 0

        stage_scores = []
        for m in milestones:
            items = m.action_items or []
            if m.is_completed:
                stage_scores.append(1.0)
            elif items:
                comp = sum(1 for it in items if it.get('completed'))
                stage_scores.append(comp / len(items))
            else:
                stage_scores.append(0.0)

        avg_score = sum(stage_scores) / total
        self.overall_progress = int(round(avg_score * 100))
        return self.overall_progress

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'target_role': self.target_role,
            'overall_progress': self.overall_progress,
            'milestones': [m.to_dict() for m in self.milestones.all()],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class RoadmapMilestone(db.Model):
    __tablename__ = 'roadmap_milestones'

    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey('career_roadmaps.id', ondelete='CASCADE'), nullable=False)
    stage_number = db.Column(db.Integer, nullable=False, default=1)
    stage_name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    action_items_json = db.Column(db.Text, nullable=True)  # JSON array of {id, text, completed}
    resources_json = db.Column(db.Text, nullable=True)     # JSON array of {title, url, type}
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    @property
    def action_items(self):
        if not self.action_items_json:
            return []
        try:
            return json.loads(self.action_items_json)
        except Exception:
            return []

    @action_items.setter
    def action_items(self, value):
        self.action_items_json = json.dumps(value if isinstance(value, list) else [])

    @property
    def resources(self):
        if not self.resources_json:
            return []
        try:
            res_list = json.loads(self.resources_json)
            for r in res_list:
                if 'neetcode' in r.get('title', '').lower():
                    r['title'] = 'LeetCode 150 Problems'
                    r['url'] = 'https://leetcode.com/studyplan/top-interview-150/'
            return res_list
        except Exception:
            return []

    @resources.setter
    def resources(self, value):
        self.resources_json = json.dumps(value if isinstance(value, list) else [])

    def to_dict(self):
        return {
            'id': self.id,
            'roadmap_id': self.roadmap_id,
            'stage_number': self.stage_number,
            'stage_name': self.stage_name,
            'title': self.title,
            'description': self.description,
            'action_items': self.action_items,
            'resources': self.resources,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.strftime('%Y-%m-%d') if self.completed_at else None
        }
