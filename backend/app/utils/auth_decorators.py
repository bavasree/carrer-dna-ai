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


def get_current_user_and_profile():
    """
    Utility to fetch the current user and their associated student profile.
    Returns (user, student_profile).
    """
    user_id = get_jwt_identity()
    if not user_id:
        return None, None

    user = User.query.get(user_id)
    if not user or not user.is_active:
        return None, None

    return user, user.profile
