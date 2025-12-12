"""Custom exceptions and DRF exception handler."""

from rest_framework.views import exception_handler


class AuthenticationException(Exception):
    """Raised when authentication fails explicitly."""


class InvalidTokenException(Exception):
    """Raised when a provided token is invalid or expired."""


class ResourceNotFoundException(Exception):
    """Raised when an expected resource cannot be located."""


class InvalidRentalPeriodException(Exception):
    """Raised when rental dates are invalid."""


class CarNotAvailableException(Exception):
    """Raised when a car is not available for the requested period."""


class RentalConflictException(Exception):
    """Raised when overlapping rentals or conflicts occur."""


class RentalException(Exception):
    """Generic rental domain exception used by tasks/services."""


def custom_exception_handler(exc, context):
    """Wrap DRF errors with a consistent envelope."""

    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'error': True,
            'message': str(exc),
            'status_code': response.status_code,
        }

        if isinstance(response.data, dict):
            custom_response_data['details'] = response.data

        response.data = custom_response_data

    return response


__all__ = [
    'AuthenticationException',
    'InvalidTokenException',
    'ResourceNotFoundException',
    'InvalidRentalPeriodException',
    'CarNotAvailableException',
    'RentalConflictException',
    'RentalException',
    'custom_exception_handler',
]
