from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .profile import StudentProfile, Skill, StudentSkill, StudentProject, StudentCertification
from .opportunity import OpportunityCategory, Opportunity, SavedOpportunity
from .analysis import CareerAnalysis
from .roadmap import CareerRoadmap, RoadmapMilestone
from .resume import Resume
from .application import Application

__all__ = [
    'db',
    'User',
    'StudentProfile',
    'Skill',
    'StudentSkill',
    'StudentProject',
    'StudentCertification',
    'OpportunityCategory',
    'Opportunity',
    'SavedOpportunity',
    'CareerAnalysis',
    'CareerRoadmap',
    'RoadmapMilestone',
    'Resume',
    'Application'
]
