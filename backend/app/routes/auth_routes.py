from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import db, User, StudentProfile
from ..utils.response import api_response, error_response
from ..utils.validators import validate_registration

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    errors = validate_registration(data)
    if errors:
        return error_response(errors[0], 400, {'errors': errors})

    email = data['email'].strip().lower()
    password = data['password']
    role = data.get('role', 'student')
    full_name = data.get('full_name', '').strip()

    if User.query.filter_by(email=email).first():
        return error_response("An account with this email already exists.", 409)

    # Create User
    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # If student, create initial profile
    if role == 'student':
        profile = StudentProfile(
            user_id=user.id,
            full_name=full_name or email.split('@')[0],
            college_name=data.get('college_name', ''),
            degree=data.get('degree', ''),
            branch=data.get('branch', ''),
            career_goal=data.get('career_goal', ''),
            target_role=data.get('target_role', '')
        )
        profile.calculate_completion_pct()
        db.session.add(profile)

    db.session.commit()

    # Issue JWT token
    additional_claims = {"role": user.role, "email": user.email}
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

    return api_response(
        data={
            "token": access_token,
            "user": user.to_dict()
        },
        message="Registration successful!",
        status_code=201
    )


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return error_response("Email and password are required.", 400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error_response("Invalid email or password.", 401)

    if not user.is_active:
        return error_response("Account is deactivated. Please contact support.", 403)

    additional_claims = {"role": user.role, "email": user.email}
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

    return api_response(
        data={
            "token": access_token,
            "user": user.to_dict()
        },
        message="Login successful!"
    )


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)

    return api_response(
        data={"user": user.to_dict()},
        message="Current user fetched successfully."
    )


@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Client removes JWT from localStorage/Cookie
    return api_response(message="Logged out successfully.")
