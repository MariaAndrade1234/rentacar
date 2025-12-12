"""
Prometheus metrics for Django/DRF monitoring.
Integrates with Prometheus for real-time monitoring and alerting.
"""

from prometheus_client import Counter, Histogram, Gauge
import time

# API Request Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Database Metrics
database_queries_total = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation', 'model']
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'model'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0)
)

# Cache Metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_name']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_name']
)

cache_size_bytes = Gauge(
    'cache_size_bytes',
    'Cache size in bytes',
    ['cache_name']
)

# Celery Metrics
celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'status']
)

celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name'],
    buckets=(1, 5, 10, 30, 60, 300)
)

celery_queue_length = Gauge(
    'celery_queue_length',
    'Celery queue length',
    ['queue_name']
)

# Business Metrics
rentals_created_total = Counter(
    'rentals_created_total',
    'Total rentals created'
)

rentals_active_gauge = Gauge(
    'rentals_active',
    'Active rentals count'
)

rental_revenue_total = Counter(
    'rental_revenue_total',
    'Total rental revenue in dollars'
)

cars_available_gauge = Gauge(
    'cars_available',
    'Available cars count'
)

# Authentication Metrics
login_attempts_total = Counter(
    'login_attempts_total',
    'Total login attempts',
    ['status']
)

active_users_gauge = Gauge(
    'active_users',
    'Active users count'
)


class PrometheusMiddleware:
    """Django middleware for Prometheus metrics."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Record metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.path
        ).observe(duration)
        
        return response
