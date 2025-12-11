from datetime import datetime, timedelta
from typing import Dict, Any


def validate_rental_dates(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """
    Validate rental date range.
    """
    errors = {}
    
    if not start_date:
        errors['start_date'] = "Start date is required"
    if not end_date:
        errors['end_date'] = "End date is required"
    
    if start_date and end_date:
        if start_date < datetime.now():
            errors['start_date'] = "Start date cannot be in the past"
        
        if end_date <= start_date:
            errors['end_date'] = "End date must be after start date"
        
        if (end_date - start_date).days < 1:
            errors['duration'] = "Minimum rental period is 1 day"
        
        if (end_date - start_date).days > 365:
            errors['duration'] = "Maximum rental period is 365 days"
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_rental_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complete rental data.
    """
    errors = {}
    
    if not data.get('customer_id'):
        errors['customer_id'] = "Customer ID is required"
    
   
    if not data.get('car_id'):
        errors['car_id'] = "Car ID is required"
    
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if start_date and end_date:
        if isinstance(start_date, str):
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                errors['start_date'] = "Invalid date format. Use ISO format (YYYY-MM-DD)"
        
        if isinstance(end_date, str):
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                errors['end_date'] = "Invalid date format. Use ISO format (YYYY-MM-DD)"
        
        if 'start_date' not in errors and 'end_date' not in errors:
            date_validation = validate_rental_dates(start_date, end_date)
            if not date_validation['valid']:
                errors.update(date_validation['errors'])
    else:
        if not start_date:
            errors['start_date'] = "Start date is required"
        if not end_date:
            errors['end_date'] = "End date is required"
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_rental_status(status: str) -> Dict[str, Any]:
    valid_statuses = ['pending', 'confirmed', 'active', 'completed', 'cancelled', 'delayed']
    errors = {}
    
    if not status:
        errors['status'] = "Status is required"
    elif status.lower() not in valid_statuses:
        errors['status'] = f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_extras(extras: list) -> Dict[str, Any]:
    valid_extras = ['insurance', 'gps', 'child_seat', 'wifi_hotspot', 'car_wash']
    errors = {}
    
    if not isinstance(extras, list):
        errors['extras'] = "Extras must be a list"
        return {'valid': False, 'errors': errors}
    
    invalid_extras = [e for e in extras if e not in valid_extras]
    if invalid_extras:
        errors['extras'] = f"Invalid extras: {', '.join(invalid_extras)}. Valid options: {', '.join(valid_extras)}"
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
