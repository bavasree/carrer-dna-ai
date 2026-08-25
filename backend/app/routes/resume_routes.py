from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Resume, StudentProfile
from ..services.gemini_service import gemini_service
from ..services.pdf_service import pdf_service
from ..utils.response import api_response, error_response

resume_bp = Blueprint('resume_bp', __name__, url_prefix='/api/resume')

def _get_or_create_resume(profile):
    resume = Resume.query.filter_by(student_id=profile.id).first()
    if not resume:
        # Build initial content data snapshot from profile
        skills = [s.skill_name for s in profile.skills.all()]
        content_data = {
            "full_name": profile.full_name,
            "headline": profile.headline or "Software Engineer",
            "email": profile.user.email if profile.user else "",
            "phone": profile.phone or "",
            "github_url": profile.github_url or "",
            "linkedin_url": profile.linkedin_url or "",
            "portfolio_url": profile.portfolio_url or "",
            "college_name": profile.college_name or "",
            "degree": profile.degree or "",
            "branch": profile.branch or "",
            "graduation_year": profile.graduation_year or 2026,
            "cgpa": profile.cgpa or 8.0,
            "skills": skills,
            "projects": [p.to_dict() for p in profile.projects.all()],
            "certifications": [c.to_dict() for c in profile.certifications.all()]
        }
        career_obj = profile.bio or f"Motivated {profile.degree or 'Computer Science'} graduate passionate about scalable software systems, seeking opportunities to contribute to high-impact technical initiatives."
        resume = Resume(
            student_id=profile.id,
            title=f"{profile.full_name}'s Resume",
            template_name='modern',
            career_objective=career_obj,
            skills_summary=", ".join(skills),
            content_data=content_data,
            ats_score=75
        )
        db.session.add(resume)
        db.session.commit()
    else:
        # Always refresh profile projects/skills in content data snapshot if empty
        cd = resume.content_data or {}
        if not cd.get('projects') and profile.projects.count() > 0:
            cd['projects'] = [p.to_dict() for p in profile.projects.all()]
            resume.content_data = cd
            db.session.commit()
    return resume


@resume_bp.route('', methods=['GET'], strict_slashes=False)
@resume_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_resume():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 400)

    resume = _get_or_create_resume(user.profile)
    return api_response(data=resume.to_dict(), message="Resume loaded successfully.")


@resume_bp.route('', methods=['PUT'], strict_slashes=False)
@resume_bp.route('/', methods=['PUT'], strict_slashes=False)
@jwt_required()
def save_resume():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 400)

    resume = _get_or_create_resume(user.profile)
    data = request.get_json() or {}

    if 'title' in data: resume.title = data['title']
    if 'template_name' in data: resume.template_name = data['template_name']
    if 'career_objective' in data: resume.career_objective = data['career_objective']
    if 'skills_summary' in data: resume.skills_summary = data['skills_summary']
    if 'content_data' in data: resume.content_data = data['content_data']

    db.session.commit()
    return api_response(data=resume.to_dict(), message="Resume saved successfully!")


@resume_bp.route('/ai-improve', methods=['POST'])
@jwt_required()
def ai_improve_section():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 400)

    data = request.get_json() or {}
    section_type = data.get('section_type', 'career_objective')
    text_content = data.get('text_content', '').strip()
    context = data.get('context', {})

    if not text_content:
        text_content = user.profile.bio or "Software engineer student with experience in web applications."

    context['target_role'] = user.profile.target_role or 'Software Engineer'
    context['degree'] = user.profile.degree
    context['branch'] = user.profile.branch

    result = gemini_service.improve_resume_section(section_type, text_content, context)
    return api_response(data=result, message="Text improved with AI.")


@resume_bp.route('/ai-score-ats', methods=['POST'])
@jwt_required()
def ai_score_ats():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.profile:
        return error_response("Student profile required", 400)

    resume = _get_or_create_resume(user.profile)
    data = request.get_json() or {}

    # Capture any live modifications sent from the editor
    if 'career_objective' in data and data['career_objective']:
        resume.career_objective = data['career_objective']
    if 'skills_summary' in data and data['skills_summary']:
        resume.skills_summary = data['skills_summary']

    target_role = data.get('target_role') or user.profile.target_role or user.profile.career_goal or 'Software Engineer'

    resume_payload = {
        "title": resume.title,
        "career_objective": resume.career_objective,
        "skills_summary": resume.skills_summary,
        "content_data": resume.content_data
    }

    ats_result = gemini_service.score_resume_ats(resume_payload, target_role)
    resume.ats_score = ats_result.get('ats_score', 75)
    resume.ats_feedback = ats_result
    db.session.commit()

    return api_response(data=ats_result, message="ATS evaluation completed successfully.")


@resume_bp.route('/download-pdf', methods=['GET'])
def download_resume_pdf():
    # Support token from Authorization header or query parameter
    token = request.args.get('token')
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]

    user_id = None
    if token:
        try:
            from flask_jwt_extended import decode_token
            decoded = decode_token(token)
            user_id = decoded.get('sub')
        except Exception:
            pass

    user = User.query.get(user_id) if user_id else None
    target_student_id = request.args.get('student_id', type=int)

    target_profile = None
    if target_student_id:
        target_profile = StudentProfile.query.get(target_student_id)
    elif user and user.profile:
        target_profile = user.profile
    elif user and user.role == 'admin':
        target_profile = StudentProfile.query.first()

    if not target_profile:
        target_profile = StudentProfile.query.first()
        if not target_profile:
            return error_response("No student profile found for resume generation.", 404)

    resume = _get_or_create_resume(target_profile)
    template = request.args.get('template', resume.template_name or 'modern')

    pdf_buffer = pdf_service.generate_resume_pdf(resume, target_profile, template=template)
    safe_name = (target_profile.full_name or 'Student').replace(' ', '_')
    filename = f"{safe_name}_Resume_{template.capitalize()}.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=filename
    )


@resume_bp.route('/student/<int:student_id>/pdf', methods=['GET'])
def download_student_resume_pdf(student_id):
    student_profile = StudentProfile.query.get(student_id)
    if not student_profile:
        return error_response("Student profile not found.", 404)

    resume = _get_or_create_resume(student_profile)
    template = request.args.get('template', resume.template_name or 'modern')

    pdf_buffer = pdf_service.generate_resume_pdf(resume, student_profile, template=template)
    safe_name = (student_profile.full_name or 'Student').replace(' ', '_')
    filename = f"{safe_name}_Resume_{template.capitalize()}.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=filename
    )
