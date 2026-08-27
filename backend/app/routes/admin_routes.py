import re
from datetime import datetime
from flask import Blueprint, request
from ..models import db, User, StudentProfile, Opportunity, OpportunityCategory, Application
from ..utils.auth_decorators import role_required
from ..utils.response import api_response, error_response

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api/admin')

DEPARTMENT_ALIASES = {
    'it': ['it', 'information technology', 'info tech', 'infotech', 'information science', 'information systems'],
    'cse': ['cse', 'cs', 'computer science', 'computer engineering', 'computer science and engineering', 'computer science & engineering', 'comp sci'],
    'ece': ['ece', 'electronics', 'electronics and communication', 'electronics & communication', 'ec', 'electronic communication'],
    'eee': ['eee', 'electrical', 'electrical and electronics', 'electrical & electronics', 'ee'],
    'mech': ['mech', 'mechanical', 'mechanical engineering'],
    'civil': ['civil', 'civil engineering'],
    'aids': ['aids', 'ai', 'ds', 'ai & ds', 'ai/ds', 'data science', 'artificial intelligence', 'artificial intelligence and data science', 'ai and data science', 'data science & ai'],
    'cys': ['cys', 'cyber', 'cyber security', 'cybersecurity', 'information security'],
    'se': ['se', 'software engineering', 'software development']
}

def match_department(filter_val, student_branch, student_degree=""):
    """
    Synonym-aware department matching between filter values and student branch/degree records.
    Handles abbreviations (IT, CSE, ECE, AIDS) and full names (Information Technology, Computer Science).
    """
    if not filter_val or filter_val.strip().lower() == 'all':
        return True
    
    f_val = filter_val.strip().lower()
    combined = f"{student_branch or ''} {student_degree or ''}".strip().lower()
    
    if not combined:
        return f_val in ['other', 'general', 'all']

    # 1. Direct clean substring matches in either direction
    if f_val in combined or combined in f_val:
        return True

    # 2. Check canonical alias groups
    for group_key, aliases in DEPARTMENT_ALIASES.items():
        filter_matches_group = any(
            alias == f_val or alias in f_val or f_val in alias
            for alias in aliases
        )
        if filter_matches_group:
            for alias in aliases:
                pattern = r'(?:\b|_)' + re.escape(alias) + r'(?:\b|_)'
                if re.search(pattern, combined) or (len(alias) >= 3 and alias in combined):
                    return True
                tokens = re.split(r'[\s/,\(\)\-]+', combined)
                if alias in tokens:
                    return True

    # 3. Fuzzy token intersection for multi-word branches
    f_tokens = [t for t in re.split(r'[\s/,\(\)\-]+', f_val) if len(t) > 2 and t not in ['and', 'engineering', 'technology', 'department', 'branch']]
    c_tokens = [t for t in re.split(r'[\s/,\(\)\-]+', combined) if len(t) > 2 and t not in ['and', 'engineering', 'technology', 'department', 'branch']]
    if any(t in c_tokens for t in f_tokens):
        return True

    return False

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_admin_stats():
    now = datetime.utcnow()
    total_users = User.query.count()
    student_count = User.query.filter_by(role='student').count()
    total_opportunities = Opportunity.query.count()
    active_opportunities = Opportunity.query.filter_by(status='active').count()
    expired_opportunities = Opportunity.query.filter(Opportunity.deadline < now, Opportunity.status == 'active').count()
    total_applications = Application.query.count()

    type_counts = {}
    opps = Opportunity.query.all()
    for o in opps:
        t = o.opportunity_type or 'other'
        type_counts[t] = type_counts.get(t, 0) + 1

    # Recent 5 registered students preview
    recent_students_query = User.query.filter_by(role='student').order_by(User.created_at.desc()).limit(5).all()
    recent_students = []
    for u in recent_students_query:
        p = u.profile
        recent_students.append({
            'id': p.id if p else None,
            'user_id': u.id,
            'full_name': p.full_name if p else u.email.split('@')[0],
            'email': u.email,
            'degree': p.degree if p else 'N/A',
            'branch': p.branch if p else 'N/A',
            'career_goal': p.career_goal or (p.target_role if p else None) or 'Software Engineer',
            'completion_pct': p.profile_completion_pct if p else 0,
            'is_active': u.is_active,
            'created_at': u.created_at.strftime('%b %d, %Y') if u.created_at else 'Recent'
        })

    return api_response(
        data={
            "total_users": total_users,
            "total_students": student_count,
            "total_opportunities": total_opportunities,
            "active_opportunities": active_opportunities,
            "expired_opportunities": expired_opportunities,
            "total_applications": total_applications,
            "type_breakdown": type_counts,
            "recent_students": recent_students
        },
        message="Admin analytics retrieved."
    )


# ==============================================================================
# Registered Students Management
# ==============================================================================
@admin_bp.route('/students', methods=['GET'])
@role_required('admin')
def list_registered_students():
    search = request.args.get('search')
    branch_filter = request.args.get('branch')
    year_filter = request.args.get('year')
    status_filter = request.args.get('status')

    query = User.query.filter_by(role='student')

    if status_filter and status_filter != 'all':
        is_act = status_filter == 'active'
        query = query.filter(User.is_active == is_act)

    users = query.order_by(User.created_at.desc()).all()
    student_list = []

    for u in users:
        p = u.profile
        name = p.full_name if p else u.email.split('@')[0]
        email = u.email
        degree = p.degree if p else ''
        branch = p.branch if p else ''
        grad_year = p.graduation_year if p else None
        cgpa = p.cgpa if p else None
        career_goal = (p.career_goal or (p.target_role if p else '')) if p else ''
        skills = [s.skill_name for s in p.skills.all()] if p else []
        apps_count = p.applications.count() if p else 0

        # Filter in python for clean text matching across skills & profile fields
        if search:
            s_term = search.strip().lower()
            match_name = s_term in name.lower()
            match_email = s_term in email.lower()
            match_branch = match_department(s_term, branch, degree) or (s_term in branch.lower())
            match_degree = s_term in degree.lower()
            match_goal = s_term in career_goal.lower()
            match_skills = any(s_term in sk.lower() for sk in skills)
            if not (match_name or match_email or match_branch or match_degree or match_goal or match_skills):
                continue

        if branch_filter and branch_filter != 'all':
            if not match_department(branch_filter, branch, degree):
                continue

        if year_filter and year_filter != 'all':
            try:
                if grad_year != int(year_filter):
                    continue
            except ValueError:
                pass

        student_list.append({
            'id': p.id if p else None,
            'user_id': u.id,
            'full_name': name,
            'email': email,
            'college_name': p.college_name if p else 'Not set',
            'degree': degree or 'N/A',
            'branch': branch or 'General',
            'graduation_year': grad_year or 'N/A',
            'cgpa': cgpa or 'N/A',
            'headline': p.headline if p else '',
            'career_goal': career_goal or 'Not specified',
            'target_role': p.target_role if p else '',
            'skills': skills,
            'profile_completion_pct': p.profile_completion_pct if p else 0,
            'applications_count': apps_count,
            'has_uploaded_resume': bool(p and p.resume_filename),
            'resume_filename': p.resume_filename if p else None,
            'resume_original_name': p.resume_original_name if p else None,
            'resume_uploaded_at': p.resume_uploaded_at.strftime('%b %d, %Y') if (p and p.resume_uploaded_at) else None,
            'resume_url': f"/api/resume/student/{p.id}/pdf" if p else None,
            'is_active': u.is_active,
            'created_at': u.created_at.strftime('%b %d, %Y') if u.created_at else 'Recent'
        })

    return api_response(
        data={
            "students": student_list,
            "total": len(student_list)
        },
        message="Registered students loaded."
    )


@admin_bp.route('/students/<int:user_id>', methods=['GET'])
@role_required('admin')
def get_student_details(user_id):
    user = User.query.get(user_id)
    if not user or user.role != 'student':
        return error_response("Student not found.", 404)

    p = user.profile
    if not p:
        return api_response(data={
            'user_id': user.id,
            'email': user.email,
            'is_active': user.is_active,
            'profile': None,
            'applications': []
        }, message="Student has no profile yet.")

    profile_dict = p.to_dict()
    apps = [a.to_dict() for a in p.applications.all()]
    skills = [s.to_dict() for s in p.skills.all()]
    projects = [proj.to_dict() for proj in p.projects.all()]

    return api_response(
        data={
            'user_id': user.id,
            'email': user.email,
            'is_active': user.is_active,
            'profile': profile_dict,
            'skills': skills,
            'projects': projects,
            'applications': apps
        },
        message="Student details retrieved."
    )


@admin_bp.route('/students/<int:user_id>/status', methods=['PUT'])
@role_required('admin')
def toggle_student_status(user_id):
    user = User.query.get(user_id)
    if not user or user.role != 'student':
        return error_response("Student not found.", 404)

    data = request.get_json() or {}
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
    else:
        user.is_active = not user.is_active

    db.session.commit()
    status_label = "activated" if user.is_active else "deactivated"
    return api_response(data={'is_active': user.is_active}, message=f"Student account {status_label}.")


@admin_bp.route('/students/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_student(user_id):
    user = User.query.get(user_id)
    if not user or user.role != 'student':
        return error_response("Student not found.", 404)

    db.session.delete(user)
    db.session.commit()
    return api_response(message="Student account deleted successfully.")


# ==============================================================================
# Opportunity Management & Expired Opportunities Cleaner
# ==============================================================================
@admin_bp.route('/opportunities', methods=['GET'])
@role_required('admin')
def list_admin_opportunities():
    status = request.args.get('status')
    opp_type = request.args.get('type')
    search = request.args.get('search')
    now = datetime.utcnow()

    query = Opportunity.query

    if status and status != 'all':
        if status == 'expired':
            query = query.filter(Opportunity.deadline < now)
        else:
            query = query.filter(Opportunity.status == status)

    if opp_type and opp_type != 'all':
        query = query.filter(Opportunity.opportunity_type == opp_type)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            (Opportunity.title.ilike(term)) |
            (Opportunity.company_name.ilike(term))
        )

    opportunities = query.order_by(Opportunity.created_at.desc()).all()

    return api_response(
        data={
            "opportunities": [o.to_dict() for o in opportunities],
            "total": len(opportunities)
        },
        message="Opportunities loaded."
    )


@admin_bp.route('/opportunities/<int:opp_id>/applicants', methods=['GET'])
@role_required('admin')
def get_opportunity_applicants(opp_id):
    """View all registered students / applicants for a specific opportunity."""
    opp = Opportunity.query.get(opp_id)
    if not opp:
        return error_response("Opportunity not found.", 404)

    applicants_list = []
    for app_entry in opp.applications.order_by(Application.created_at.desc()).all():
        student_profile = app_entry.student
        user = student_profile.user if student_profile else None
        student_name = student_profile.full_name if (student_profile and student_profile.full_name) else (user.email.split('@')[0] if user else 'Student')
        skills_list = [s.skill_name for s in student_profile.skills.all()] if student_profile else []
        applicants_list.append({
            'application_id': app_entry.id,
            'student_id': student_profile.id if student_profile else None,
            'user_id': user.id if user else None,
            'name': student_name,
            'email': user.email if user else '',
            'phone': student_profile.phone if student_profile else '',
            'college': student_profile.college_name if student_profile else '',
            'degree': student_profile.degree if student_profile else '',
            'branch': student_profile.branch if student_profile else '',
            'skills': skills_list,
            'career_goal': student_profile.career_goal if student_profile else '',
            'status': app_entry.status,
            'applied_date': app_entry.applied_date.strftime('%b %d, %Y') if app_entry.applied_date else 'N/A',
            'notes': app_entry.notes or '',
            'headline': student_profile.headline if student_profile else '',
            'submitted_details': app_entry.submitted_details,
            'resume_filename': app_entry.resume_filename,
            'resume_url': app_entry.to_dict().get('resume_url')
        })

    return api_response(
        data={
            "opportunity": opp.to_dict(),
            "applicants": applicants_list,
            "total_applicants": len(applicants_list)
        },
        message=f"Retrieved {len(applicants_list)} applicants for {opp.title}."
    )


@admin_bp.route('/opportunities', methods=['POST'])
@role_required('admin')
def create_opportunity():
    data = request.get_json() or {}

    title = (data.get('title') or '').strip()
    company_name = (data.get('company_name') or '').strip()
    opp_type = (data.get('opportunity_type') or '').strip().lower()
    description = (data.get('description') or '').strip()
    apply_url = (data.get('apply_url') or '').strip()

    if not title or not company_name or not opp_type or not description or not apply_url:
        return error_response("Title, company, type, description, and apply URL are required.", 400)

    deadline = None
    if data.get('deadline'):
        try:
            deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
        except ValueError:
            pass

    opp = Opportunity(
        title=title,
        company_name=company_name,
        opportunity_type=opp_type,
        description=description,
        apply_url=apply_url,
        category_id=data.get('category_id'),
        location=data.get('location', 'Remote'),
        is_remote=bool(data.get('is_remote', True)),
        stipend_salary=data.get('stipend_salary', ''),
        deadline=deadline,
        required_skills=data.get('required_skills', []),
        eligibility_criteria=data.get('eligibility_criteria', ''),
        status=data.get('status', 'active'),
        experience_level=data.get('experience_level', 'Any')
    )
    db.session.add(opp)
    db.session.commit()

    return api_response(data=opp.to_dict(), message="Opportunity created successfully!", status_code=201)


@admin_bp.route('/opportunities/<int:opp_id>', methods=['PUT'])
@role_required('admin')
def update_opportunity(opp_id):
    opp = Opportunity.query.get(opp_id)
    if not opp:
        return error_response("Opportunity not found.", 404)

    data = request.get_json() or {}
    if 'title' in data: opp.title = data['title']
    if 'company_name' in data: opp.company_name = data['company_name']
    if 'opportunity_type' in data: opp.opportunity_type = data['opportunity_type']
    if 'description' in data: opp.description = data['description']
    if 'apply_url' in data: opp.apply_url = data['apply_url']
    if 'category_id' in data: opp.category_id = data['category_id']
    if 'location' in data: opp.location = data['location']
    if 'is_remote' in data: opp.is_remote = bool(data['is_remote'])
    if 'stipend_salary' in data: opp.stipend_salary = data['stipend_salary']
    if 'eligibility_criteria' in data: opp.eligibility_criteria = data['eligibility_criteria']
    if 'status' in data: opp.status = data['status']
    if 'experience_level' in data: opp.experience_level = data['experience_level']
    if 'required_skills' in data: opp.required_skills = data['required_skills']

    if 'deadline' in data:
        if not data['deadline']:
            opp.deadline = None
        else:
            try:
                opp.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
            except ValueError:
                pass

    db.session.commit()
    return api_response(data=opp.to_dict(), message="Opportunity updated successfully.")


@admin_bp.route('/opportunities/<int:opp_id>', methods=['GET'])
@role_required('admin')
def get_single_opportunity(opp_id):
    opp = Opportunity.query.get(opp_id)
    if not opp:
        return error_response("Opportunity not found.", 404)
    return api_response(data=opp.to_dict(), message="Opportunity details retrieved.")


@admin_bp.route('/opportunities/<int:opp_id>', methods=['DELETE'])
@role_required('admin')
def delete_opportunity(opp_id):
    opp = Opportunity.query.get(opp_id)
    if not opp:
        return error_response("Opportunity not found.", 404)

    # Cleanly dissociate student applications before deleting opportunity
    Application.query.filter_by(opportunity_id=opp_id).update({'opportunity_id': None}, synchronize_session=False)
    db.session.delete(opp)
    db.session.commit()
    return api_response(message="Opportunity deleted permanently.")


@admin_bp.route('/opportunities/clean-expired', methods=['POST'])
@role_required('admin')
def clean_expired_opportunities():
    """
    Finds opportunities where the deadline is in the past and automatically
    archives or removes them based on the requested action ('archive' or 'delete').
    """
    data = request.get_json() or {}
    action = data.get('action', 'archive') # 'archive' or 'delete'
    now = datetime.utcnow()

    expired_opps = Opportunity.query.filter(Opportunity.deadline < now).all()
    count = len(expired_opps)

    if count == 0:
        return api_response(data={'count': 0}, message="No expired opportunities found. Catalog is up to date!")

    if action == 'delete':
        for o in expired_opps:
            db.session.delete(o)
        db.session.commit()
        return api_response(data={'count': count}, message=f"Permanently removed {count} expired opportunities.")
    else:
        for o in expired_opps:
            o.status = 'closed'
        db.session.commit()
        return api_response(data={'count': count}, message=f"Marked {count} expired opportunities as closed/archived.")


@admin_bp.route('/opportunities/bulk-status', methods=['POST'])
@role_required('admin')
def bulk_status_update():
    data = request.get_json() or {}
    ids = data.get('ids', [])
    new_status = data.get('status', 'active')

    if not ids:
        return error_response("List of opportunity IDs required.", 400)

    Opportunity.query.filter(Opportunity.id.in_(ids)).update({'status': new_status}, synchronize_session=False)
    db.session.commit()

    return api_response(message=f"Updated status to '{new_status}' for {len(ids)} opportunities.")


# ==============================================================================
# All Applications & Registrations Monitoring
# ==============================================================================
@admin_bp.route('/applications', methods=['GET'])
@role_required('admin')
def list_all_applications():
    """
    Returns all student applications and registrations across the platform with filtering and search.
    """
    search = request.args.get('search', '').strip().lower()
    type_filter = request.args.get('type', '').strip().lower()
    status_filter = request.args.get('status', '').strip().lower()

    query = Application.query.order_by(Application.created_at.desc())

    if type_filter and type_filter != 'all':
        query = query.filter(Application.opportunity_type == type_filter)

    if status_filter and status_filter != 'all':
        query = query.filter(Application.status == status_filter)

    apps = query.all()
    results = []

    for a in apps:
        student_profile = a.student
        user = student_profile.user if student_profile else None
        student_name = student_profile.full_name if (student_profile and student_profile.full_name) else (user.email.split('@')[0] if user else 'Student')
        student_email = user.email if user else ''
        student_phone = student_profile.phone if student_profile else ''

        # Search filter across student name, email, opportunity title, and company
        if search:
            match_name = search in student_name.lower()
            match_email = search in student_email.lower()
            match_opp = search in (a.position_title or '').lower()
            match_comp = search in (a.company_name or '').lower()
            match_notes = search in (a.notes or '').lower()
            if not (match_name or match_email or match_opp or match_comp or match_notes):
                continue

        results.append({
            'id': a.id,
            'student_id': student_profile.id if student_profile else None,
            'user_id': user.id if user else None,
            'student_name': student_name,
            'student_email': student_email,
            'student_phone': student_phone,
            'college_name': student_profile.college_name if student_profile else 'University Student',
            'degree': student_profile.degree if student_profile else 'Degree',
            'skills': [s.skill_name for s in student_profile.skills.all()] if student_profile else [],
            'opportunity_id': a.opportunity_id,
            'opportunity_title': a.position_title,
            'company_name': a.company_name,
            'opportunity_type': a.opportunity_type,
            'status': a.status,
            'applied_date': a.applied_date.strftime('%b %d, %Y') if a.applied_date else 'N/A',
            'deadline': a.deadline.strftime('%b %d, %Y') if a.deadline else None,
            'notes': a.notes or '',
            'submitted_details': a.submitted_details,
            'resume_filename': a.resume_filename,
            'resume_url': a.to_dict().get('resume_url')
        })

    return api_response(
        data={
            "applications": results,
            "total_count": len(results)
        },
        message="Applications retrieved successfully."
    )


@admin_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@role_required('admin')
def update_application_status(app_id):
    """
    Admin endpoint to advance or update a student's application stage.
    """
    app_entry = Application.query.get(app_id)
    if not app_entry:
        return error_response("Application not found.", 404)

    data = request.get_json() or {}
    new_status = data.get('status', '').strip().lower()

    if not new_status:
        return error_response("New status is required.", 400)

    app_entry.status = new_status
    db.session.commit()

    return api_response(
        data=app_entry.to_dict(),
        message=f"Application stage updated to '{new_status.replace('_', ' ').title()}'."
    )
