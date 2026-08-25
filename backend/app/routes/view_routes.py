from flask import Blueprint, render_template

view_bp = Blueprint('view_bp', __name__)

@view_bp.route('/')
def index():
    return render_template('index.html')

@view_bp.route('/login')
def login_page():
    return render_template('login.html')

@view_bp.route('/register')
def register_page():
    return render_template('register.html')

@view_bp.route('/onboarding')
def onboarding_page():
    return render_template('onboarding.html')

@view_bp.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@view_bp.route('/profile')
def profile_page():
    return render_template('profile.html')

@view_bp.route('/career-analysis')
def career_analysis_page():
    return render_template('career_analysis.html')

@view_bp.route('/recommendations')
def recommendations_page():
    return render_template('recommendations.html')

@view_bp.route('/roadmap')
def roadmap_page():
    return render_template('roadmap.html')

@view_bp.route('/resume-builder')
def resume_builder_page():
    return render_template('resume_builder.html')

@view_bp.route('/applications')
def applications_page():
    return render_template('applications.html')

@view_bp.route('/admin')
@view_bp.route('/admin/dashboard')
def admin_dashboard_page():
    return render_template('admin/dashboard.html')

@view_bp.route('/admin/opportunities')
def admin_opportunities_page():
    return render_template('admin/opportunities.html')

@view_bp.route('/admin/students')
def admin_students_page():
    return render_template('admin/students.html')

@view_bp.route('/admin/applications')
def admin_applications_page():
    return render_template('admin/applications.html')

