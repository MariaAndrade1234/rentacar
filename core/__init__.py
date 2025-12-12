"""
Celery app initialization.
Import this in __init__.py to ensure Celery is loaded when Django starts.
"""

from .celery import app as celery_app

__all__ = ('celery_app',)
