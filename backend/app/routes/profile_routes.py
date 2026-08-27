import os
from datetime import datetime
from flask import Blueprint, request, current_app, send_from_directory
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, StudentProfile, StudentSkill, StudentProject, StudentCertification, Skill
from ..utils.response import api_response, error_response
from ..utils.validators import validate_profile

profile_bp = Blueprint('profile_bp', __name__, url_prefix='/api/profile')

def _get_student_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return None
    if not user.profile:
        # Auto-create empty profile
        profile = StudentProfile(
            user_id=user.id,
            full_name=user.email.split('@')[0]
        )
        db.session.add(profile)
        db.session.commit()
    return user.profile


@profile_bp.route('', methods=['GET'], strict_slashes=False)
@profile_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    if not profile:
        return error_response("Profile not found", 404)

    profile.calculate_completion_pct()
    db.session.commit()

    return api_response(data=profile.to_dict(), message="Profile fetched successfully.")


@profile_bp.route('', methods=['PUT'], strict_slashes=False)
@profile_bp.route('/', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    if not profile:
        return error_response("Profile not found", 404)

    data = request.get_json() or {}
    errors = validate_profile(data)
    if errors:
        return error_response(errors[0], 400, {'errors': errors})

    # Update direct fields
    updatable_fields = [
        'full_name', 'headline', 'phone', 'college_name', 'degree', 'branch',
        'graduation_year', 'cgpa', 'bio', 'career_goal', 'target_role',
        'github_url', 'linkedin_url', 'portfolio_url'
    ]

    for field in updatable_fields:
        if field in data:
            setattr(profile, field, data[field])

    if 'interests' in data:
        if isinstance(data['interests'], list):
            profile.interests = ", ".join(data['interests'])
        else:
            profile.interests = str(data['interests'])

    profile.calculate_completion_pct()
    db.session.commit()

    return api_response(data=profile.to_dict(), message="Profile updated successfully!")


@profile_bp.route('/skills', methods=['POST'])
@jwt_required()
def add_skill():
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    if not profile:
        return error_response("Profile not found", 404)

    data = request.get_json() or {}
    skill_name = (data.get('skill_name') or '').strip()
    proficiency = data.get('proficiency_level', 'intermediate')
    years_exp = float(data.get('years_of_experience', 1.0))

    if not skill_name:
        return error_response("Skill name is required.", 400)

    # Check if already added
    existing = StudentSkill.query.filter_by(student_id=profile.id, skill_name=skill_name).first()
    if existing:
        existing.proficiency_level = proficiency
        existing.years_of_experience = years_exp
        db.session.commit()
        profile.calculate_completion_pct()
        db.session.commit()
        return api_response(data=existing.to_dict(), message="Skill updated successfully.")

    # Match or create catalog skill
    cat_skill = Skill.query.filter(Skill.name.ilike(skill_name)).first()
    skill_id = cat_skill.id if cat_skill else None

    new_skill = StudentSkill(
        student_id=profile.id,
        skill_id=skill_id,
        skill_name=skill_name,
        proficiency_level=proficiency,
        years_of_experience=years_exp
    )
    db.session.add(new_skill)
    profile.calculate_completion_pct()
    db.session.commit()

    return api_response(data=new_skill.to_dict(), message="Skill added successfully!", status_code=201)


@profile_bp.route('/skills/<int:skill_id>', methods=['DELETE'])
@jwt_required()
def delete_skill(skill_id):
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    skill = StudentSkill.query.filter_by(id=skill_id, student_id=profile.id).first()
    if not skill:
        return error_response("Skill not found.", 404)

    db.session.delete(skill)
    profile.calculate_completion_pct()
    db.session.commit()

    return api_response(message="Skill removed successfully.")


@profile_bp.route('/projects', methods=['POST'])
@jwt_required()
def add_project():
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    data = request.get_json() or {}

    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()

    if not title or not description:
        return error_response("Project title and description are required.", 400)

    project = StudentProject(
        student_id=profile.id,
        title=title,
        description=description,
        tech_stack=data.get('tech_stack', ''),
        github_url=data.get('github_url', ''),
        live_url=data.get('live_url', ''),
        role=data.get('role', '')
    )
    db.session.add(project)
    profile.calculate_completion_pct()
    db.session.commit()

    return api_response(data=project.to_dict(), message="Project added successfully!", status_code=201)


@profile_bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    project = StudentProject.query.filter_by(id=project_id, student_id=profile.id).first()
    if not project:
        return error_response("Project not found.", 404)

    data = request.get_json() or {}
    project.title = data.get('title', project.title)
    project.description = data.get('description', project.description)
    project.tech_stack = data.get('tech_stack', project.tech_stack)
    project.github_url = data.get('github_url', project.github_url)
    project.live_url = data.get('live_url', project.live_url)
    project.role = data.get('role', project.role)

    db.session.commit()
    return api_response(data=project.to_dict(), message="Project updated successfully.")


@profile_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    project = StudentProject.query.filter_by(id=project_id, student_id=profile.id).first()
    if not project:
        return error_response("Project not found.", 404)

    db.session.delete(project)
    profile.calculate_completion_pct()
    db.session.commit()

    return api_response(message="Project deleted successfully.")


@profile_bp.route('/certifications', methods=['POST'])
@jwt_required()
def add_certification():
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    data = request.get_json() or {}

    title = (data.get('title') or '').strip()
    issuing_org = (data.get('issuing_organization') or '').strip()

    if not title or not issuing_org:
        return error_response("Certification title and issuing organization are required.", 400)

    cert = StudentCertification(
        student_id=profile.id,
        title=title,
        issuing_organization=issuing_org,
        issue_date=data.get('issue_date', ''),
        credential_id=data.get('credential_id', ''),
        credential_url=data.get('credential_url', '')
    )
    db.session.add(cert)
    profile.calculate_completion_pct()
    db.session.commit()

    return api_response(data=cert.to_dict(), message="Certification added successfully!", status_code=201)


@profile_bp.route('/certifications/<int:cert_id>', methods=['DELETE'])
@jwt_required()
def delete_certification(cert_id):
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    cert = StudentCertification.query.filter_by(id=cert_id, student_id=profile.id).first()
    if not cert:
        return error_response("Certification not found.", 404)

    db.session.delete(cert)
    profile.calculate_completion_pct()
    db.session.commit()

    return api_response(message="Certification removed successfully.")


@profile_bp.route('/skills-catalog', methods=['GET'])
def get_skills_catalog():
    skills = Skill.query.all()
    return api_response(data=[s.to_dict() for s in skills], message="Skills catalog fetched.")


ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx'}

def _is_allowed_resume_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_RESUME_EXTENSIONS


@profile_bp.route('/resume', methods=['POST'])
@jwt_required()
def upload_profile_resume():
    """Upload and attach a real student resume file to student's profile."""
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    if not profile:
        return error_response("Profile not found.", 404)

    file = request.files.get('resume') or request.files.get('resume_file') or request.files.get('file')
    if not file or not file.filename:
        return error_response("No resume file uploaded. Please select a PDF or DOCX file.", 400)

    if not _is_allowed_resume_file(file.filename):
        return error_response("Invalid file format. Only PDF, DOC, and DOCX files are allowed.", 400)

    upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static', 'uploads', 'resumes'))
    os.makedirs(upload_dir, exist_ok=True)

    orig_name = secure_filename(file.filename)
    if not orig_name:
        orig_name = f"resume_{profile.id}.pdf"
    
    timestamp = int(datetime.utcnow().timestamp())
    unique_filename = f"resume_{profile.id}_{timestamp}_{orig_name}"
    file_path = os.path.join(upload_dir, unique_filename)

    try:
        file.save(file_path)
    except Exception as e:
        return error_response(f"Failed to save resume file: {str(e)}", 500)

    # Clean up old file if exists
    if profile.resume_filename:
        old_path = os.path.join(upload_dir, profile.resume_filename)
        if os.path.exists(old_path) and profile.resume_filename != unique_filename:
            try:
                os.remove(old_path)
            except Exception:
                pass

    profile.resume_filename = unique_filename
    profile.resume_original_name = file.filename
    profile.resume_uploaded_at = datetime.utcnow()
    profile.calculate_completion_pct()
    db.session.commit()

    return api_response(
        data=profile.to_dict(),
        message="Resume uploaded and attached to your profile successfully!",
        status_code=200
    )


@profile_bp.route('/resume', methods=['GET'])
@jwt_required()
def get_profile_resume():
    """Download/view current student's attached resume."""
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    if not profile or not profile.resume_filename:
        return error_response("No resume attached to profile.", 404)

    upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static', 'uploads', 'resumes'))
    file_path = os.path.join(upload_dir, profile.resume_filename)

    if not os.path.exists(file_path):
        return error_response("Uploaded resume file not found on server.", 404)

    return send_from_directory(
        upload_dir,
        profile.resume_filename,
        download_name=profile.resume_original_name or profile.resume_filename,
        as_attachment=False
    )


@profile_bp.route('/resume', methods=['DELETE'])
@jwt_required()
def delete_profile_resume():
    """Remove attached resume from student's profile."""
    user_id = get_jwt_identity()
    profile = _get_student_profile(user_id)
    if not profile:
        return error_response("Profile not found.", 404)

    if profile.resume_filename:
        upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static', 'uploads', 'resumes'))
        file_path = os.path.join(upload_dir, profile.resume_filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    profile.resume_filename = None
    profile.resume_original_name = None
    profile.resume_uploaded_at = None
    profile.calculate_completion_pct()
    db.session.commit()

    return api_response(data=profile.to_dict(), message="Attached resume removed successfully.")

