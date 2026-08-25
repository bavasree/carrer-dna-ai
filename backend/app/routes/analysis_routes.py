from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, CareerAnalysis
from ..services.gemini_service import gemini_service
from ..utils.response import api_response, error_response

analysis_bp = Blueprint('analysis_bp', __name__, url_prefix='/api/career-analysis')

@analysis_bp.route('', methods=['GET'], strict_slashes=False)
@analysis_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_latest_analysis():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 404)

    latest = CareerAnalysis.query.filter_by(student_id=user.profile.id).order_by(CareerAnalysis.created_at.desc()).first()
    if not latest:
        return api_response(data=None, message="No analysis generated yet. Run your first AI Career Analysis!")

    return api_response(data=latest.to_dict(), message="Latest career analysis fetched.")


@analysis_bp.route('/analyze', methods=['POST'])
@jwt_required()
def run_career_analysis():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required to run AI analysis", 400)

    profile = user.profile
    profile_data = profile.to_dict()

    # Call Gemini service (with automatic heuristic fallback)
    ai_result = gemini_service.analyze_career(profile_data)

    analysis = CareerAnalysis(
        student_id=profile.id,
        readiness_score=ai_result.get('readiness_score', 50),
        strengths=ai_result.get('strengths', []),
        weaknesses=ai_result.get('weaknesses', []),
        skill_gaps=ai_result.get('skill_gaps', []),
        recommended_roles=ai_result.get('recommended_roles', []),
        recommended_certifications=ai_result.get('recommended_certifications', []),
        recommended_technologies=ai_result.get('recommended_technologies', []),
        ai_summary=ai_result.get('ai_summary', '')
    )
    db.session.add(analysis)
    db.session.commit()

    return api_response(
        data=analysis.to_dict(),
        message="AI Career Analysis completed successfully!",
        status_code=201
    )


@analysis_bp.route('/skill-gap', methods=['POST'])
@jwt_required()
def run_skill_gap_analysis():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 400)

    data = request.get_json() or {}
    target_role = data.get('target_role') or user.profile.target_role or user.profile.career_goal or 'Software Engineer'

    profile_data = user.profile.to_dict()
    result = gemini_service.analyze_skill_gap(profile_data, target_role)

    return api_response(data=result, message="Skill gap analysis completed.")
