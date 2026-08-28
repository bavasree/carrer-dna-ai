from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from ..models import User, StudentProfile
from .response import error_response

def role_required(*allowed_roles):
    """
    Decorator to protect routes by user role (e.g., 'admin', 'student').
    Extracts role from JWT claims or queries database.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception as e:
                return error_response(f"Authentication required: {str(e)}", 401)

            claims = get_jwt()
            user_role = claims.get('role')

            if not user_role:
                # Fallback to querying user
                user_id = get_jwt_identity()
                user = User.query.get(user_id)
                if not user or not user.is_active:
                    return error_response("User not found or inactive", 401)
                user_role = user.role

            if user_role not in allowed_roles:
                return error_response(
                    f"Forbidden: Requires one of following roles: {', '.join(allowed_roles)}",
                    403
                )

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_student_profile(user_id=None):
    """
    Robust student profile retriever for both local and serverless environments.
    Handles integer casting, auto-creation of missing profiles, and JWT claims recovery.
    """
    from ..models import db
    if not user_id:
        try:
            user_id = get_jwt_identity()
        except Exception:
            pass

    if not user_id:
        return None

    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        uid = user_id

    # 1. Try finding StudentProfile directly by user_id
    profile = StudentProfile.query.filter_by(user_id=uid).first()
    if profile:
        return profile

    # 2. Try finding User by ID
    user = User.query.get(uid)

    # 3. If User not found by ID, try JWT claims fallback (email)
    claims = {}
    try:
        claims = get_jwt() or {}
        email = claims.get('email')
        if not user and email:
            user = User.query.filter_by(email=email.strip().lower()).first()
    except Exception:
        pass

    # 4. If User STILL not found (e.g. fresh ephemeral serverless instance), recreate User
    if not user:
        email = (claims.get('email') or f"student_{uid}@careerdna.ai").strip().lower()
        role = claims.get('role', 'student')
        try:
            user = User(
                email=email,
                role=role
            )
            user.set_password('temporary_serverless_session_pass')
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            user = User.query.filter_by(email=email).first()

    if not user:
        return None

    # 5. If user exists, ensure profile exists
    if not user.profile:
        try:
            profile = StudentProfile(
                user_id=user.id,
                full_name=user.email.split('@')[0].replace('.', ' ').title()
            )
            profile.calculate_completion_pct()
            db.session.add(profile)
            db.session.commit()
            return profile
        except Exception:
            db.session.rollback()
            return StudentProfile.query.filter_by(user_id=user.id).first()

    return user.profile


def get_current_user_and_profile():
    """
    Utility to fetch the current user and their associated student profile.
    Returns (user, student_profile).
    """
    profile = get_student_profile()
    if not profile:
        return None, None
    user = profile.user
    return user, profile
