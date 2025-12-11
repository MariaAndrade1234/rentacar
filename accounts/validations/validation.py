"""
Validation functions for accounts app.
"""

import re
from typing import Dict, Any


def validate_email(email: str) -> bool:
    """
    Validate email format.
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def validate_username(username: str) -> bool:
    """
    Validate username format.
    Username must be 3-30 characters, alphanumeric and underscores only.
    """
    if not username or len(username) < 3 or len(username) > 30:
        return False
    username_pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(username_pattern, username))


def validate_password(password: str) -> Dict[str, Any]:
    """
    Validate password strength.
    Returns a dict with 'valid' boolean and 'errors' list.
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_account_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complete account data.
    Returns a dict with 'valid' boolean and 'errors' dict.
    """
    errors = {}
    
    if 'email' in data and not validate_email(data['email']):
        errors['email'] = "Invalid email format"
    
    if 'username' in data and not validate_username(data['username']):
        errors['username'] = "Invalid username format"
    
    if 'password' in data:
        password_validation = validate_password(data['password'])
        if not password_validation['valid']:
            errors['password'] = password_validation['errors']
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
