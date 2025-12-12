"""
Elasticsearch integration for centralized logging.
ELK Stack (Elasticsearch, Logstash, Kibana) setup.
"""

import logging
from pythonjsonlogger import jsonlogger
from elasticsearch import Elasticsearch
from datetime import datetime


class ElasticsearchHandler(logging.Handler):
    """Custom logging handler that sends logs to Elasticsearch."""
    
    def __init__(self, hosts=['localhost:9200'], index_prefix='rentacar'):
        super().__init__()
        self.es = Elasticsearch(hosts=hosts)
        self.index_prefix = index_prefix
    
    def emit(self, record):
        try:
            # Format log as JSON
            log_entry = {
                'timestamp': datetime.utcnow(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'thread': record.thread,
                'thread_name': record.threadName,
                'process': record.process,
            }
            
            # Add exception info if present
            if record.exc_info:
                log_entry['exception'] = self.format(record)
            
            # Add extra fields
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'created', 'filename', 
                               'funcName', 'levelname', 'levelno', 'lineno', 
                               'module', 'msecs', 'message', 'pathname', 'process',
                               'processName', 'relativeCreated', 'thread', 
                               'threadName', 'exc_info', 'exc_text', 'stack_info']:
                    log_entry[key] = value
            
            # Send to Elasticsearch
            index_name = f"{self.index_prefix}-{datetime.utcnow().strftime('%Y.%m.%d')}"
            self.es.index(index=index_name, doc_type='_doc', body=log_entry)
        
        except Exception:
            self.handleError(record)


# Elasticsearch configuration for Django logging
ELASTICSEARCH_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(timestamp)s %(level)s %(logger)s %(message)s'
        },
    },
    'handlers': {
        'elasticsearch': {
            '()': 'core.elasticsearch_handler.ElasticsearchHandler',
            'hosts': ['localhost:9200'],
            'index_prefix': 'rentacar',
            'formatter': 'json',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'rentals': {
            'handlers': ['console', 'elasticsearch'],
            'level': 'INFO',
        },
        'authentication': {
            'handlers': ['console', 'elasticsearch'],
            'level': 'INFO',
        },
        'cars': {
            'handlers': ['console', 'elasticsearch'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console', 'elasticsearch'],
            'level': 'ERROR',
        },
    },
}
