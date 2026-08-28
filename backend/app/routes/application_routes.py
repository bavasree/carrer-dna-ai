import os
import uuid
import json
from datetime import datetime
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Application, Opportunity
from ..utils.response import api_response, error_response
from ..utils.auth_decorators import get_student_profile

application_bp = Blueprint('application_bp', __name__, url_prefix='/api/applications')

ALLOWED_RESUME_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

def allowed_resume_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_RESUME_EXTENSIONS

# ==============================================================================
# Opportunity-Type Specific Workflows Definition
# ==============================================================================
WORKFLOW_CONFIG = {
    'job': {
        'label': 'Job',
        'default_status': 'applied',
        'stages': [
            {'key': 'applied', 'label': 'Applied', 'icon': 'bi-send', 'color': 'primary'},
            {'key': 'screening', 'label': 'Screening', 'icon': 'bi-funnel', 'color': 'info'},
            {'key': 'interview', 'label': 'Interview', 'icon': 'bi-calendar2-check', 'color': 'warning'},
            {'key': 'offer', 'label': 'Offer', 'icon': 'bi-trophy', 'color': 'success'},
            {'key': 'rejected', 'label': 'Rejected', 'icon': 'bi-x-circle', 'color': 'danger'}
        ]
    },
    'internship': {
        'label': 'Internship',
        'default_status': 'applied',
        'stages': [
            {'key': 'applied', 'label': 'Applied', 'icon': 'bi-send', 'color': 'primary'},
            {'key': 'screening', 'label': 'Screening', 'icon': 'bi-funnel', 'color': 'info'},
            {'key': 'interview', 'label': 'Interview', 'icon': 'bi-calendar2-check', 'color': 'warning'},
            {'key': 'offer', 'label': 'Offer', 'icon': 'bi-trophy', 'color': 'success'},
            {'key': 'rejected', 'label': 'Rejected', 'icon': 'bi-x-circle', 'color': 'danger'}
        ]
    },
    'hackathon': {
        'label': 'Hackathon',
        'default_status': 'registered',
        'stages': [
            {'key': 'registered', 'label': 'Registered', 'icon': 'bi-clipboard-check', 'color': 'primary'},
            {'key': 'shortlisted', 'label': 'Shortlisted', 'icon': 'bi-funnel', 'color': 'info'},
            {'key': 'round_1', 'label': 'Round 1', 'icon': 'bi-flag', 'color': 'warning'},
            {'key': 'round_2', 'label': 'Round 2', 'icon': 'bi-lightning', 'color': 'secondary'},
            {'key': 'finalist', 'label': 'Finalist', 'icon': 'bi-stars', 'color': 'accent-purple'},
            {'key': 'winner', 'label': 'Winner', 'icon': 'bi-trophy', 'color': 'success'},
            {'key': 'not_selected', 'label': 'Not Selected', 'icon': 'bi-x-circle', 'color': 'danger'}
        ]
    },
    'competition': {
        'label': 'Competition',
        'default_status': 'registered',
        'stages': [
            {'key': 'registered', 'label': 'Registered', 'icon': 'bi-clipboard-check', 'color': 'primary'},
            {'key': 'participating', 'label': 'Participating', 'icon': 'bi-play-circle', 'color': 'info'},
            {'key': 'qualified', 'label': 'Qualified', 'icon': 'bi-patch-check', 'color': 'warning'},
            {'key': 'final_round', 'label': 'Final Round', 'icon': 'bi-stars', 'color': 'accent-purple'},
            {'key': 'winner', 'label': 'Winner', 'icon': 'bi-trophy', 'color': 'success'},
            {'key': 'not_selected', 'label': 'Not Selected', 'icon': 'bi-x-circle', 'color': 'danger'}
        ]
    },
    'certification': {
        'label': 'Certification',
        'default_status': 'enrolled',
        'stages': [
            {'key': 'enrolled', 'label': 'Enrolled', 'icon': 'bi-journal-check', 'color': 'primary'},
            {'key': 'in_progress', 'label': 'In Progress', 'icon': 'bi-hourglass-split', 'color': 'info'},
            {'key': 'completed', 'label': 'Certified', 'icon': 'bi-award', 'color': 'success'},
            {'key': 'expired', 'label': 'Incomplete / Expired', 'icon': 'bi-x-circle', 'color': 'danger'}
        ]
    },
    'course': {
        'label': 'Course',
        'default_status': 'enrolled',
        'stages': [
            {'key': 'enrolled', 'label': 'Enrolled', 'icon': 'bi-journal-check', 'color': 'primary'},
            {'key': 'in_progress', 'label': 'In Progress', 'icon': 'bi-hourglass-split', 'color': 'info'},
            {'key': 'completed', 'label': 'Completed', 'icon': 'bi-award', 'color': 'success'},
            {'key': 'expired', 'label': 'Dropped / Expired', 'icon': 'bi-x-circle', 'color': 'danger'}
        ]
    },
    'workshop': {
        'label': 'Workshop & Bootcamp',
        'default_status': 'registered',
        'stages': [
            {'key': 'registered', 'label': 'RSVP Confirmed', 'icon': 'bi-ticket-perforated', 'color': 'primary'},
            {'key': 'attending', 'label': 'Attending', 'icon': 'bi-camera-video', 'color': 'info'},
            {'key': 'completed', 'label': 'Masterclass Certified', 'icon': 'bi-patch-check', 'color': 'success'},
            {'key': 'cancelled', 'label': 'Cancelled / Missed', 'icon': 'bi-x-circle', 'color': 'danger'}
        ]
    },
    'other': {
        'label': 'Other Opportunity',
        'default_status': 'registered',
        'stages': [
            {'key': 'registered', 'label': 'Registered', 'icon': 'bi-send', 'color': 'primary'},
            {'key': 'in_progress', 'label': 'In Progress', 'icon': 'bi-hourglass-split', 'color': 'info'},
            {'key': 'completed', 'label': 'Selected / Completed', 'icon': 'bi-trophy', 'color': 'success'},
            {'key': 'not_selected', 'label': 'Not Selected', 'icon': 'bi-x-circle', 'color': 'danger'}
        ]
    }
}

ALL_KNOWN_STAGES = {
    'applied', 'screening', 'interview', 'interview_scheduled', 'offer', 'rejected',
    'registered', 'shortlisted', 'round_1', 'round_2', 'finalist', 'winner', 'not_selected',
    'participating', 'qualified', 'final_round', 'enrolled', 'in_progress', 'completed', 'expired'
}

def normalize_status(opp_type, status):
    """Normalize legacy or alias statuses to the canonical workflow keys."""
    t = (opp_type or 'job').lower()
    cfg = WORKFLOW_CONFIG.get(t, WORKFLOW_CONFIG['job'])
    valid_keys = {stg['key'] for stg in cfg['stages']}

    if not status:
        return cfg['default_status']

    if status in valid_keys:
        return status

    # Backward compatible aliases
    if status in ['interview_scheduled', 'interview']:
        return 'interview' if 'interview' in valid_keys else ('interview_scheduled' if 'interview_scheduled' in valid_keys else cfg['default_status'])
    if status == 'in_progress':
        if 'screening' in valid_keys: return 'screening'
        if 'participating' in valid_keys: return 'participating'
        if 'in_progress' in valid_keys: return 'in_progress'
    if status in ['applied', 'registered', 'enrolled']:
        if 'registered' in valid_keys and t in ['hackathon', 'competition']: return 'registered'
        if 'enrolled' in valid_keys and t in ['certification', 'course']: return 'enrolled'
        if 'applied' in valid_keys: return 'applied'
    if status in ['rejected', 'not_selected', 'expired']:
        if 'not_selected' in valid_keys: return 'not_selected'
        if 'expired' in valid_keys: return 'expired'
        if 'rejected' in valid_keys: return 'rejected'
    if status in ['offer', 'winner', 'completed']:
        if 'winner' in valid_keys: return 'winner'
        if 'completed' in valid_keys: return 'completed'
        if 'offer' in valid_keys: return 'offer'

    # Fallback to default status for this workflow
    return cfg['default_status']


def auto_update_application_statuses(student_id):
    """
    Automated status evaluation engine:
    - Automatically updates statuses based on interview dates, deadlines, and opportunity status.
    - Synchronizes application deadlines and details with linked Opportunity records.
    """
    apps = Application.query.filter_by(student_id=student_id).all()
    today = datetime.utcnow().date()
    changed = False

    for app in apps:
        opp_type = (app.opportunity_type or 'job').lower()
        if opp_type not in WORKFLOW_CONFIG:
            opp_type = 'other'

        # Rule 1: Normalize legacy status strings
        normalized = normalize_status(opp_type, app.status)
        if normalized != app.status:
            app.status = normalized
            changed = True

        # Rule 2: If interview_date is set and status is applied/screening/registered -> auto advance to interview
        if app.interview_date and opp_type in ['job', 'internship']:
            if app.status in ['applied', 'screening']:
                app.status = 'interview'
                changed = True

        # Rule 3: Sync deadline from linked Opportunity if application has no deadline
        if app.opportunity_id:
            opp = Opportunity.query.get(app.opportunity_id)
            if opp and opp.deadline:
                opp_date = opp.deadline.date() if hasattr(opp.deadline, 'date') else opp.deadline
                if not app.deadline:
                    app.deadline = opp_date
                    changed = True

    if changed:
        db.session.commit()


@application_bp.route('/workflows', methods=['GET'])
def get_workflows():
    """Returns the type-aware workflow schemas for the frontend."""
    return api_response(data=WORKFLOW_CONFIG, message="Workflows retrieved.")


@application_bp.route('', methods=['GET'], strict_slashes=False)
@application_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def list_applications():
    user_id = get_jwt_identity()
    profile = get_student_profile(user_id)
    if not profile:
        return error_response("Student profile required", 400)

    # Trigger automatic status updates & synchronization
    auto_update_application_statuses(profile.id)

    # Opportunity type filter
    filter_type = request.args.get('type')
    query = Application.query.filter_by(student_id=profile.id)
    if filter_type and filter_type != 'all':
        query = query.filter_by(opportunity_type=filter_type)

    apps = query.order_by(Application.created_at.desc()).all()

    # Build Kanban structures: both legacy standard 5-stage mapping and type-aware structures
    # 1. Standard / Combined Kanban mapping for backwards compatibility and "All" view
    standard_kanban = {
        'applied': [],
        'in_progress': [],
        'interview_scheduled': [],
        'offer': [],
        'rejected': []
    }

    # 2. Type-grouped Kanban
    type_kanban = {}
    for t, cfg in WORKFLOW_CONFIG.items():
        type_kanban[t] = {stg['key']: [] for stg in cfg['stages']}

    for a in apps:
        data = a.to_dict()
        opp_type = (a.opportunity_type or 'job').lower()
        if opp_type not in type_kanban:
            opp_type = 'other'

        # Place into type-aware Kanban
        stg_key = a.status if a.status in type_kanban[opp_type] else WORKFLOW_CONFIG[opp_type]['default_status']
        type_kanban[opp_type][stg_key].append(data)

        # Place into standard combined Kanban
        std_key = a.status
        if std_key in ['registered', 'enrolled', 'applied']:
            std_key = 'applied'
        elif std_key in ['screening', 'participating', 'shortlisted', 'round_1', 'round_2', 'in_progress']:
            std_key = 'in_progress'
        elif std_key in ['interview', 'interview_scheduled', 'qualified', 'final_round', 'finalist']:
            std_key = 'interview_scheduled'
        elif std_key in ['offer', 'winner', 'completed']:
            std_key = 'offer'
        elif std_key in ['rejected', 'not_selected', 'expired']:
            std_key = 'rejected'
        else:
            std_key = 'applied'

        standard_kanban[std_key].append(data)

    return api_response(
        data={
            "applications": [a.to_dict() for a in apps],
            "kanban": standard_kanban,
            "type_kanban": type_kanban,
            "workflows": WORKFLOW_CONFIG,
            "total_count": len(apps)
        },
        message="Applications retrieved successfully."
    )


@application_bp.route('', methods=['POST'], strict_slashes=False)
@application_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_application():
    user_id = get_jwt_identity()
    profile = get_student_profile(user_id)
    if not profile:
        return error_response("Student profile required", 400)

    data = request.get_json() or {}
    company_name = (data.get('company_name') or '').strip()
    position_title = (data.get('position_title') or '').strip()
    opp_type = (data.get('opportunity_type') or 'job').lower()
    if opp_type not in WORKFLOW_CONFIG:
        opp_type = 'job'

    opp_id = data.get('opportunity_id')
    opp_deadline = None
    if opp_id:
        existing = Application.query.filter_by(student_id=profile.id, opportunity_id=opp_id).first()
        if existing:
            return error_response(
                f"You have already registered / applied for this opportunity! Current stage: {existing.status.replace('_', ' ').title()}.",
                409
            )
        opp = Opportunity.query.get(opp_id)
        if opp:
            if not company_name: company_name = opp.company_name
            if not position_title: position_title = opp.title
            if opp.opportunity_type: opp_type = opp.opportunity_type.lower()
            if opp.deadline: opp_deadline = opp.deadline.date() if hasattr(opp.deadline, 'date') else opp.deadline

    if not company_name or not position_title:
        return error_response("Company name and position title are required.", 400)

    # Date parsing
    applied_date = datetime.utcnow().date()
    if data.get('applied_date'):
        try:
            applied_date = datetime.strptime(data['applied_date'], '%Y-%m-%d').date()
        except ValueError:
            pass

    interview_date = None
    if data.get('interview_date'):
        try:
            interview_date = datetime.strptime(data['interview_date'], '%Y-%m-%d %H:%M')
        except ValueError:
            try:
                interview_date = datetime.strptime(data['interview_date'], '%Y-%m-%d')
            except ValueError:
                pass

    deadline = opp_deadline
    if data.get('deadline'):
        try:
            deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
        except ValueError:
            pass

    # Status handling: default to type's initial status if not specified
    raw_status = data.get('status')
    if not raw_status:
        initial_status = WORKFLOW_CONFIG[opp_type]['default_status']
    else:
        initial_status = normalize_status(opp_type, raw_status)

    # Auto-detect interview status if interview date is present
    if interview_date and opp_type in ['job', 'internship'] and initial_status in ['applied', 'screening']:
        initial_status = 'interview'

    app_entry = Application(
        student_id=user.profile.id,
        opportunity_id=opp_id,
        company_name=company_name,
        position_title=position_title,
        opportunity_type=opp_type,
        status=initial_status,
        applied_date=applied_date,
        interview_date=interview_date,
        deadline=deadline,
        notes=data.get('notes', ''),
        salary_offered=data.get('salary_offered', '')
    )
    db.session.add(app_entry)
    db.session.commit()

    return api_response(data=app_entry.to_dict(), message="Application tracked successfully!", status_code=201)


@application_bp.route('/apply', methods=['POST'])
@jwt_required()
def apply_for_opportunity():
    """
    Real-world Opportunity-Specific Student Application & Registration Engine:
    - Supports JSON and Multipart Form Data (Resume File Uploads)
    - Validates student profile and opportunity existence
    - Prevents duplicate registrations with friendly status notice
    - Captures comprehensive opportunity-type specific details
    - Saves uploaded resume file or AI-generated resume attachment
    - Automatically assigns type-aware initial workflow status
    - Records detailed metadata in database and synchronizes with Application Tracker
    """
    user_id = get_jwt_identity()
    profile = get_student_profile(user_id)
    if not profile:
        return error_response("Student profile required to register or apply for opportunities.", 400)

    # Determine if request is multipart form data or JSON
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()
        # Parse any JSON-stringified arrays/objects
        if 'skills' in data and isinstance(data['skills'], str):
            try:
                data['skills'] = json.loads(data['skills'])
            except Exception:
                data['skills'] = [s.strip() for s in data['skills'].split(',') if s.strip()]

    opp_id = data.get('opportunity_id')
    if not opp_id:
        return error_response("Opportunity ID is required.", 400)

    try:
        opp_id = int(opp_id)
    except (ValueError, TypeError):
        return error_response("Invalid Opportunity ID.", 400)

    opp = Opportunity.query.get(opp_id)
    if not opp:
        return error_response("Opportunity not found.", 404)

    # 1. Prevent duplicate registration
    existing = Application.query.filter_by(student_id=profile.id, opportunity_id=opp.id).first()
    if existing:
        stage_title = existing.status.replace('_', ' ').title()
        return error_response(
            f"You have already registered / applied for this opportunity! (Current Status: {stage_title}). Check your Application Tracker to monitor your progress.",
            409
        )

    opp_type = (opp.opportunity_type or 'job').lower()
    if opp_type not in WORKFLOW_CONFIG:
        opp_type = 'other'

    initial_status = WORKFLOW_CONFIG[opp_type]['default_status']

    # 2. Handle Resume File Upload or AI Resume selection
    resume_filename = None
    resume_source = data.get('resume_source', 'profile')

    if 'resume_file' in request.files:
        file = request.files['resume_file']
        if file and file.filename and allowed_resume_file(file.filename):
            orig_name = secure_filename(file.filename)
            unique_name = f"resume_{profile.id}_{int(datetime.utcnow().timestamp())}_{orig_name}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            try:
                file.save(save_path)
                resume_filename = unique_name
                # Also save as student profile attached resume if not already set
                if not profile.resume_filename:
                    profile.resume_filename = unique_name
                    profile.resume_original_name = file.filename
                    profile.resume_uploaded_at = datetime.utcnow()
                    profile.calculate_completion_pct()
                    db.session.commit()
            except Exception as e:
                pass

    if not resume_filename:
        if resume_source == 'ai_generated':
            resume_filename = 'ai_generated'
        elif profile.resume_filename:
            # Attach the student's actual uploaded profile resume
            resume_filename = profile.resume_filename
        elif data.get('resume_url'):
            resume_filename = data.get('resume_url')

    # 3. Structure Opportunity-Type Specific Submitted Details
    submitted_details = {
        'candidate': {
            'full_name': data.get('full_name') or profile.full_name,
            'email': data.get('email') or user.email,
            'phone': data.get('phone') or profile.phone or '',
            'college_name': data.get('college_name') or profile.college_name or '',
            'department': data.get('department') or profile.branch or profile.degree or '',
            'degree': data.get('degree') or profile.degree or '',
            'year_of_study': data.get('year_of_study') or profile.graduation_year or '',
            'cgpa': data.get('cgpa') or profile.cgpa or '',
            'skills': data.get('skills') if isinstance(data.get('skills'), list) else (profile.skills.all() if hasattr(profile.skills, 'all') else []),
            'github_url': data.get('github_url') or profile.github_url or '',
            'linkedin_url': data.get('linkedin_url') or profile.linkedin_url or '',
            'portfolio_url': data.get('portfolio_url') or profile.portfolio_url or ''
        },
        'opportunity_type': opp_type,
        'opportunity_title': opp.title,
        'company_name': opp.company_name,
        'applied_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Ensure skills are strings
    if isinstance(submitted_details['candidate']['skills'], list):
        submitted_details['candidate']['skills'] = [
            s.skill_name if hasattr(s, 'skill_name') else str(s)
            for s in submitted_details['candidate']['skills']
        ]

    # Type-specific payload compilation
    summary_notes = []

    if opp_type == 'hackathon':
        team_name = data.get('team_name', '').strip()
        team_size = data.get('team_size', 'Individual')
        team_members = data.get('team_members', '').strip()
        hack_exp = data.get('hackathon_experience', 'First-time Participant')
        project_idea = data.get('project_idea', '').strip()
        track = data.get('project_track', '').strip()
        dietary = data.get('dietary_requirements', '').strip()
        tshirt = data.get('tshirt_size', '').strip()

        submitted_details['hackathon_details'] = {
            'team_name': team_name or 'Solo Participant',
            'team_size': team_size,
            'team_members': team_members,
            'experience': hack_exp,
            'track': track,
            'project_idea': project_idea,
            'dietary_requirements': dietary,
            'tshirt_size': tshirt
        }
        if team_name: summary_notes.append(f"Team: {team_name} ({team_size})")
        if track: summary_notes.append(f"Track: {track}")
        if project_idea: summary_notes.append(f"Idea: {project_idea[:100]}...")

    elif opp_type == 'internship':
        availability = data.get('availability', 'Immediate')
        work_mode = data.get('preferred_work_mode', 'Remote / Flexible')
        pref_location = data.get('preferred_location', opp.location or 'Remote')
        relevant_projects = data.get('relevant_projects', '').strip()
        cover_note = data.get('cover_note', '').strip()

        submitted_details['internship_details'] = {
            'availability': availability,
            'preferred_work_mode': work_mode,
            'preferred_location': pref_location,
            'relevant_projects': relevant_projects,
            'cover_note': cover_note,
            'resume_source': resume_source
        }
        summary_notes.append(f"Availability: {availability} | Work Mode: {work_mode}")
        if cover_note: summary_notes.append(f"Note: {cover_note[:120]}...")

    elif opp_type == 'job':
        exp_years = data.get('work_experience_years', 'Fresh Graduate / Entry Level')
        prev_roles = data.get('previous_company_roles', '').strip()
        curr_loc = data.get('current_location', '').strip()
        pref_loc = data.get('preferred_location', opp.location or 'Flexible')
        notice = data.get('notice_period', 'Immediate')
        salary_exp = data.get('expected_salary', opp.stipend_salary or '')
        cover_letter = data.get('cover_letter', '').strip()

        submitted_details['job_details'] = {
            'experience_years': exp_years,
            'previous_roles': prev_roles,
            'current_location': curr_loc,
            'preferred_location': pref_loc,
            'notice_period': notice,
            'expected_salary': salary_exp,
            'cover_letter': cover_letter,
            'resume_source': resume_source
        }
        summary_notes.append(f"Experience: {exp_years} | Notice: {notice}")
        if salary_exp: summary_notes.append(f"Expected: {salary_exp}")
        if cover_letter: summary_notes.append(f"Letter: {cover_letter[:120]}...")

    elif opp_type == 'competition':
        team_name = data.get('team_name', '').strip()
        team_members = data.get('team_members', '').strip()
        track = data.get('competition_track', '').strip()
        comp_exp = data.get('relevant_experience', '').strip()
        strategy = data.get('strategy_pitch', '').strip()

        submitted_details['competition_details'] = {
            'team_name': team_name or 'Solo Competitor',
            'team_members': team_members,
            'track': track,
            'experience': comp_exp,
            'strategy_pitch': strategy
        }
        if team_name: summary_notes.append(f"Team: {team_name}")
        if track: summary_notes.append(f"Track: {track}")
        if strategy: summary_notes.append(f"Pitch: {strategy[:100]}...")

    elif opp_type == 'workshop':
        att_mode = data.get('attendance_mode', 'In-Person')
        motivation = data.get('motivation', '').strip()

        submitted_details['workshop_details'] = {
            'attendance_mode': att_mode,
            'motivation': motivation
        }
        summary_notes.append(f"Format: {att_mode}")
        if motivation: summary_notes.append(f"Q&A Note: {motivation[:100]}...")

    else:  # certification / course / other
        schedule = data.get('learning_schedule', 'Flexible / Self-paced')
        target_date = data.get('target_completion', '')
        motivation = data.get('motivation', '').strip()

        submitted_details['course_details'] = {
            'learning_schedule': schedule,
            'target_completion': target_date,
            'motivation': motivation
        }
        if schedule: summary_notes.append(f"Schedule: {schedule}")
        if motivation: summary_notes.append(f"Goal: {motivation[:100]}...")

    final_notes = " | ".join(summary_notes) if summary_notes else f"Registered for {opp.title}"

    applied_date = datetime.utcnow().date()
    deadline = opp.deadline.date() if (opp.deadline and hasattr(opp.deadline, 'date')) else None

    # 4. Create and persist the Application
    app_entry = Application(
        student_id=profile.id,
        opportunity_id=opp.id,
        company_name=opp.company_name,
        position_title=opp.title,
        opportunity_type=opp_type,
        status=initial_status,
        applied_date=applied_date,
        deadline=deadline,
        notes=final_notes,
        submitted_details_json=json.dumps(submitted_details),
        resume_filename=resume_filename
    )
    db.session.add(app_entry)
    db.session.commit()

    type_success_messages = {
        'hackathon': f"Registration confirmed for {opp.title}! Track your team and round progression in your Application Tracker.",
        'competition': f"Registration confirmed for {opp.title}! Your entry has been submitted.",
        'internship': f"Application submitted successfully for {opp.title} at {opp.company_name}!",
        'job': f"Job application submitted successfully for {opp.title} at {opp.company_name}!",
        'certification': f"Enrolled in {opp.title} certification successfully!",
        'course': f"Enrolled in {opp.title} course successfully!",
        'workshop': f"RSVP confirmed for {opp.title}! Your ticket has been saved."
    }
    success_msg = type_success_messages.get(opp_type, f"Application for {opp.title} submitted successfully!")

    return api_response(
        data={
            "application": app_entry.to_dict(),
            "workflow": WORKFLOW_CONFIG.get(opp_type, {}),
            "initial_stage": initial_status,
            "submitted_details": submitted_details
        },
        message=success_msg,
        status_code=201
    )


@application_bp.route('/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application_detail(app_id):
    """Retrieve full details of a specific student application including submitted form data."""
    user_id = get_jwt_identity()
    profile = get_student_profile(user_id)
    if not profile:
        return error_response("Student profile required", 400)

    app_entry = Application.query.filter_by(id=app_id, student_id=profile.id).first()
    if not app_entry:
        return error_response("Application not found", 404)

    return api_response(
        data=app_entry.to_dict(),
        message="Application details retrieved successfully."
    )


@application_bp.route('/<int:app_id>', methods=['PUT'])
@jwt_required()
def update_application(app_id):
    user_id = get_jwt_identity()
    profile = get_student_profile(user_id)
    if not profile:
        return error_response("Student profile required", 400)

    app_entry = Application.query.filter_by(id=app_id, student_id=profile.id).first()
    if not app_entry:
        return error_response("Application not found", 404)

    data = request.get_json() or {}
    if 'company_name' in data: app_entry.company_name = data['company_name']
    if 'position_title' in data: app_entry.position_title = data['position_title']
    if 'opportunity_type' in data:
        new_type = data['opportunity_type'].lower()
        if new_type in WORKFLOW_CONFIG:
            app_entry.opportunity_type = new_type

    opp_type = (app_entry.opportunity_type or 'job').lower()

    if 'status' in data:
        app_entry.status = normalize_status(opp_type, data['status'])

    if 'notes' in data: app_entry.notes = data['notes']
    if 'salary_offered' in data: app_entry.salary_offered = data['salary_offered']

    if 'deadline' in data:
        if not data['deadline']:
            app_entry.deadline = None
        else:
            try:
                app_entry.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
            except ValueError:
                pass

    if 'interview_date' in data:
        if not data['interview_date']:
            app_entry.interview_date = None
        else:
            try:
                app_entry.interview_date = datetime.strptime(data['interview_date'], '%Y-%m-%d %H:%M')
            except ValueError:
                try:
                    app_entry.interview_date = datetime.strptime(data['interview_date'], '%Y-%m-%d')
                except ValueError:
                    pass

    # Automatic advancement: if user set an interview_date for a job/internship, auto set to interview if still at initial stages
    if app_entry.interview_date and opp_type in ['job', 'internship'] and app_entry.status in ['applied', 'screening']:
        app_entry.status = 'interview'

    db.session.commit()
    return api_response(data=app_entry.to_dict(), message="Application updated.")


@application_bp.route('/<int:app_id>', methods=['DELETE'])
@jwt_required()
def delete_application(app_id):
    user_id = get_jwt_identity()
    profile = get_student_profile(user_id)
    if not profile:
        return error_response("Student profile required", 400)

    app_entry = Application.query.filter_by(id=app_id, student_id=profile.id).first()
    if not app_entry:
        return error_response("Application not found", 404)

    db.session.delete(app_entry)
    db.session.commit()
    return api_response(message="Application deleted successfully.")


@application_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_application_stats():
    user_id = get_jwt_identity()
    profile = get_student_profile(user_id)
    if not profile:
        return error_response("Student profile required", 400)

    # Auto sync before statistics calculation
    auto_update_application_statuses(profile.id)

    apps = Application.query.filter_by(student_id=profile.id).all()
    total = len(apps)

    status_counts = {
        'applied': 0,
        'in_progress': 0,
        'interview_scheduled': 0,
        'offer': 0,
        'rejected': 0
    }

    type_counts = {}
    active_count = 0
    advanced_count = 0
    success_count = 0

    for a in apps:
        st = a.status
        t = (a.opportunity_type or 'job').lower()
        type_counts[t] = type_counts.get(t, 0) + 1

        # Categorize active pipeline
        if st not in ['rejected', 'not_selected', 'expired', 'offer', 'winner', 'completed']:
            active_count += 1

        # Categorize interview / advanced round rate
        if st in ['interview', 'interview_scheduled', 'round_1', 'round_2', 'finalist', 'qualified', 'final_round', 'offer', 'winner', 'completed']:
            advanced_count += 1

        # Categorize offers / wins / certifications
        if st in ['offer', 'winner', 'completed']:
            success_count += 1

        # Standard bucket counts
        if st in ['applied', 'registered', 'enrolled']:
            status_counts['applied'] += 1
        elif st in ['in_progress', 'screening', 'participating', 'shortlisted']:
            status_counts['in_progress'] += 1
        elif st in ['interview', 'interview_scheduled', 'round_1', 'round_2', 'finalist', 'qualified', 'final_round']:
            status_counts['interview_scheduled'] += 1
        elif st in ['offer', 'winner', 'completed']:
            status_counts['offer'] += 1
        elif st in ['rejected', 'not_selected', 'expired']:
            status_counts['rejected'] += 1
        else:
            status_counts['applied'] += 1

    advancement_rate = round((advanced_count / total * 100), 1) if total > 0 else 0
    offer_rate = round((success_count / total * 100), 1) if total > 0 else 0

    return api_response(
        data={
            "total_applications": total,
            "active_pipeline": active_count,
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "interview_rate": advancement_rate,
            "offer_rate": offer_rate
        },
        message="Application statistics computed."
    )


@application_bp.route('/<int:app_id>/resume', methods=['GET'])
def view_application_resume(app_id):
    """Serve the student's attached resume file or generate verified resume PDF without auth blocks."""
    from flask import current_app, send_from_directory, send_file
    import os

    app_entry = Application.query.get(app_id)
    if not app_entry:
        return error_response("Application record not found.", 404)

    # Check for static/uploaded resume file
    if app_entry.resume_filename and app_entry.resume_filename != 'ai_generated':
        upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static', 'uploads', 'resumes'))
        file_path = os.path.join(upload_dir, app_entry.resume_filename)
        if os.path.exists(file_path):
            return send_from_directory(upload_dir, app_entry.resume_filename)

    student_profile = app_entry.student
    if not student_profile:
        return error_response("Student profile associated with application not found.", 404)

    # Check if student has uploaded a resume in their profile
    if student_profile.resume_filename:
        upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static', 'uploads', 'resumes'))
        file_path = os.path.join(upload_dir, student_profile.resume_filename)
        if os.path.exists(file_path):
            return send_from_directory(
                upload_dir,
                student_profile.resume_filename,
                download_name=student_profile.resume_original_name or student_profile.resume_filename
            )

    from ..routes.resume_routes import _get_or_create_resume
    from ..services.pdf_service import pdf_service

    resume = _get_or_create_resume(student_profile)
    pdf_buffer = pdf_service.generate_resume_pdf(resume, student_profile, template='modern')
    safe_name = (student_profile.full_name or 'Student').replace(' ', '_')
    filename = f"{safe_name}_Application_{app_id}_Resume.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=filename
    )
