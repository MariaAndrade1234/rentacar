"""
Utility functions for authentication module.
Provides helper functions for extracting client information from requests.
"""


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_info(request) -> str:
    return request.META.get('HTTP_USER_AGENT', '')[:255]
