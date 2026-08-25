from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, CareerRoadmap, RoadmapMilestone
from ..services.gemini_service import gemini_service
from ..utils.response import api_response, error_response

roadmap_bp = Blueprint('roadmap_bp', __name__, url_prefix='/api/roadmap')

@roadmap_bp.route('', methods=['GET'], strict_slashes=False)
@roadmap_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_roadmap():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 400)

    profile = user.profile
    roadmap = CareerRoadmap.query.filter_by(student_id=profile.id).order_by(CareerRoadmap.created_at.desc()).first()

    if not roadmap:
        # Auto-generate first roadmap
        target_role = profile.target_role or profile.career_goal or 'Full-Stack Software Engineer'
        roadmap = _create_new_roadmap(profile, target_role)

    roadmap.calculate_progress()
    db.session.commit()

    return api_response(data=roadmap.to_dict(), message="Roadmap fetched successfully.")


@roadmap_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_custom_roadmap():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 400)

    data = request.get_json() or {}
    target_role = data.get('target_role') or user.profile.target_role or user.profile.career_goal or 'Software Engineer'

    roadmap = _create_new_roadmap(user.profile, target_role)
    return api_response(data=roadmap.to_dict(), message=f"Personalized Career Roadmap for {target_role} generated!", status_code=201)


def _create_new_roadmap(profile, target_role):
    # Archive/remove prior active roadmaps if any
    old_roadmaps = CareerRoadmap.query.filter_by(student_id=profile.id).all()
    for old_r in old_roadmaps:
        db.session.delete(old_r)
    db.session.flush()

    roadmap = CareerRoadmap(student_id=profile.id, target_role=target_role, overall_progress=0)
    db.session.add(roadmap)
    db.session.flush()

    stages_data = gemini_service.generate_roadmap(profile.to_dict(), target_role)

    for stg in stages_data:
        m = RoadmapMilestone(
            roadmap_id=roadmap.id,
            stage_number=stg.get('stage_number', 1),
            stage_name=stg.get('stage_name', f"Stage {stg.get('stage_number')}"),
            title=stg.get('title', 'Milestone Goal'),
            description=stg.get('description', ''),
            action_items=stg.get('action_items', []),
            resources=stg.get('resources', []),
            is_completed=stg.get('is_completed', False)
        )
        db.session.add(m)

    roadmap.calculate_progress()
    db.session.commit()
    return roadmap


@roadmap_bp.route('/milestones/<int:milestone_id>', methods=['PUT'])
@jwt_required()
def update_milestone(milestone_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 400)

    milestone = RoadmapMilestone.query.get(milestone_id)
    if not milestone or milestone.roadmap.student_id != user.profile.id:
        return error_response("Milestone not found or access denied.", 404)

    data = request.get_json() or {}
    if 'is_completed' in data:
        milestone.is_completed = bool(data['is_completed'])
        milestone.completed_at = datetime.utcnow() if milestone.is_completed else None
        
        # When milestone is toggled done, update all its action items
        items = milestone.action_items or []
        for it in items:
            it['completed'] = milestone.is_completed
        milestone.action_items = items

    elif 'action_items' in data:
        milestone.action_items = data['action_items']
        items = milestone.action_items or []
        # If all action items are checked, mark milestone completed
        if items and all(it.get('completed') for it in items):
            milestone.is_completed = True
            milestone.completed_at = datetime.utcnow()
        elif items and any(not it.get('completed') for it in items):
            milestone.is_completed = False
            milestone.completed_at = None

    roadmap = milestone.roadmap
    roadmap.calculate_progress()
    db.session.commit()

    return api_response(
        data={
            "milestone": milestone.to_dict(),
            "overall_progress": roadmap.overall_progress
        },
        message="Milestone updated successfully."
    )
