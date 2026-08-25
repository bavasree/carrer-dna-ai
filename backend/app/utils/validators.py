import re

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def validate_email(email):
    if not email or not isinstance(email, str):
        return False
    return bool(re.match(EMAIL_REGEX, email.strip()))


def validate_password(password):
    """Checks that password is at least 6 characters."""
    if not password or not isinstance(password, str):
        return False
    return len(password) >= 6


def validate_registration(data):
    """Validates user registration payload."""
    errors = []
    if not data:
        return ["Request body is missing or not JSON"]

    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'student')
    full_name = data.get('full_name', '').strip()

    if not validate_email(email):
        errors.append("A valid email address is required.")
    if not validate_password(password):
        errors.append("Password must be at least 6 characters long.")
    if role not in ['student', 'admin']:
        errors.append("Role must be either 'student' or 'admin'.")
    if role == 'student' and not full_name:
        errors.append("Full name is required for student registration.")

    return errors


def validate_profile(data):
    """Validates student profile update payload."""
    errors = []
    if not data:
        return ["Request payload is missing"]

    if 'full_name' in data and not data['full_name'].strip():
        errors.append("Full name cannot be empty.")

    if 'cgpa' in data and data['cgpa'] is not None and data['cgpa'] != '':
        try:
            cgpa = float(data['cgpa'])
            if cgpa < 0 or cgpa > 10:
                errors.append("CGPA must be between 0.0 and 10.0.")
        except ValueError:
            errors.append("CGPA must be a valid number.")

    if 'graduation_year' in data and data['graduation_year'] is not None and data['graduation_year'] != '':
        try:
            year = int(data['graduation_year'])
            if year < 1980 or year > 2040:
                errors.append("Graduation year must be a realistic year (1980-2040).")
        except ValueError:
            errors.append("Graduation year must be a valid integer.")

    return errors
