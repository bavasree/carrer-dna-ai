from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Opportunity, SavedOpportunity
from ..services.recommendation_engine import recommendation_engine
from ..services.gemini_service import gemini_service
from ..utils.response import api_response, error_response

recommendation_bp = Blueprint('recommendation_bp', __name__, url_prefix='/api/recommendations')

@recommendation_bp.route('', methods=['GET'], strict_slashes=False)
@recommendation_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required(optional=True)
def list_recommendations():
    user_id = get_jwt_identity()
    profile = None
    if user_id:
        user = User.query.get(user_id)
        if user:
            profile = user.profile

    filters = {
        'type': request.args.get('type'),
        'category_id': request.args.get('category_id'),
        'is_remote': request.args.get('is_remote'),
        'mode': request.args.get('mode'),
        'fee': request.args.get('fee'),
        'stipend': request.args.get('stipend'),
        'location': request.args.get('location'),
        'skills': request.args.get('skills'),
        'deadline_status': request.args.get('deadline_status'),
        'query': request.args.get('query'),
        'min_match': request.args.get('min_match', 0),
        'sort_by': request.args.get('sort_by', 'match_desc')
    }
    limit = int(request.args.get('limit', 60))

    results = recommendation_engine.get_recommendations(profile=profile, filters=filters, limit=limit)

    return api_response(
        data={
            "opportunities": results,
            "total_count": len(results),
            "filters": filters
        },
        message="Recommendations retrieved successfully."
    )


@recommendation_bp.route('/<int:opp_id>', methods=['GET'])
@jwt_required(optional=True)
def get_opportunity_details(opp_id):
    opp = Opportunity.query.get(opp_id)
    if not opp:
        return error_response("Opportunity not found", 404)

    user_id = get_jwt_identity()
    student_id = None
    match_info = {}

    if user_id:
        user = User.query.get(user_id)
        if user and user.profile:
            student_id = user.profile.id
            match_info = gemini_service.calculate_match_score(user.profile.to_dict(), opp.to_dict(student_id=student_id))

    opp_data = opp.to_dict(student_id=student_id)
    opp_data.update(match_info)

    return api_response(data=opp_data, message="Opportunity details fetched.")


@recommendation_bp.route('/<int:opp_id>/save', methods=['POST'])
@jwt_required()
def save_opportunity(opp_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 400)

    opp = Opportunity.query.get(opp_id)
    if not opp:
        return error_response("Opportunity not found", 404)

    existing = SavedOpportunity.query.filter_by(student_id=user.profile.id, opportunity_id=opp.id).first()
    if not existing:
        saved = SavedOpportunity(student_id=user.profile.id, opportunity_id=opp.id)
        db.session.add(saved)
        db.session.commit()

    return api_response(message="Opportunity bookmarked successfully.")


@recommendation_bp.route('/<int:opp_id>/save', methods=['DELETE'])
@jwt_required()
def unsave_opportunity(opp_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 400)

    saved = SavedOpportunity.query.filter_by(student_id=user.profile.id, opportunity_id=opp_id).first()
    if saved:
        db.session.delete(saved)
        db.session.commit()

    return api_response(message="Opportunity removed from bookmarks.")


@recommendation_bp.route('/saved', methods=['GET'])
@jwt_required()
def get_saved_opportunities():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 400)

    saved_items = SavedOpportunity.query.filter_by(student_id=user.profile.id).order_by(SavedOpportunity.saved_at.desc()).all()
    results = []
    for item in saved_items:
        if item.opportunity:
            data = item.opportunity.to_dict(student_id=user.profile.id)
            score_data = gemini_service.calculate_match_score(user.profile.to_dict(), data)
            data.update(score_data)
            results.append(data)

    return api_response(data={"saved_opportunities": results}, message="Saved opportunities fetched.")
