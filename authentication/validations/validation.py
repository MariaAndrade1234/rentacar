import re
from typing import Dict, Any


def validate_login_data(data: Dict[str, Any]) -> Dict[str, Any]:
    errors = {}
    
    if not data.get('username'):
        errors['username'] = "Username is required"
    
    if not data.get('password'):
        errors['password'] = "Password is required"
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_registration_data(data: Dict[str, Any]) -> Dict[str, Any]:
    errors = {}
    
    username = data.get('username', '')
    if not username:
        errors['username'] = "Username is required"
    elif len(username) < 3:
        errors['username'] = "Username must be at least 3 characters"
    elif not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors['username'] = "Username can only contain letters, numbers, and underscores"
    
    email = data.get('email', '')
    if not email:
        errors['email'] = "Email is required"
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors['email'] = "Invalid email format"
    
    password = data.get('password', '')
    if not password:
        errors['password'] = "Password is required"
    elif len(password) < 8:
        errors['password'] = "Password must be at least 8 characters"
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_password_change(data: Dict[str, Any]) -> Dict[str, Any]:
    errors = {}
    
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not old_password:
        errors['old_password'] = "Old password is required"
    
    if not new_password:
        errors['new_password'] = "New password is required"
    elif len(new_password) < 8:
        errors['new_password'] = "Password must be at least 8 characters"
    
    if new_password != confirm_password:
        errors['confirm_password'] = "Passwords do not match"
    
    if old_password == new_password:
        errors['new_password'] = "New password must be different from old password"
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_password_reset(data: Dict[str, Any]) -> Dict[str, Any]:
    errors = {}
    
    email = data.get('email', '')
    if not email:
        errors['email'] = "Email is required"
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors['email'] = "Invalid email format"
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
