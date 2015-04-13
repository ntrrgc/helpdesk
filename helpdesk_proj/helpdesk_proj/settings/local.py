from .base import *

DEBUG = True

TEMPLATE_DEBUG = False

SECRET_KEY = 'dummy key'

SNORKY_BACKEND_URL = 'http://localhost:5002/backend'

SNORKY_FRONTEND_URL = 'ws://localhost:5001/websocket'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s %(name)s %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': 'ext://sys.stdout'
        },
    },
    'loggers': {
        'snorky': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
