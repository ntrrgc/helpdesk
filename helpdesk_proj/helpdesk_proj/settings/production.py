from .base import *

DEBUG = False

TEMPLATE_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, './db.sqlite3'),
    }
}

ALLOWED_HOSTS = ALTERNATIVE_DOMAINS

SITE_URL = [
    'http://helpdesk.rufian.eu',
    'https://helpdesk.rufian.eu',
]

ADMINS = (
    ('Helpdesk admin', 'ntrrgc@gmail.com'),
)

STATIC_ROOT = 'static/'

STATIC_URL = '/static/'


SNORKY_BACKEND_URL = 'http://localhost:5002/backend'

SNORKY_FRONTEND_URL = 'wss://<HOST>/websocket'

SECRET_FILE = os.path.join(os.path.dirname(__file__), 'secret.key')

try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except IOError:
    import os, stat
    import django.utils.crypto
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    with open(SECRET_FILE, 'w') as f:
        SECRET_KEY = django.utils.crypto.get_random_string(50, chars)
        os.fchmod(f.fileno(), stat.S_IRUSR)
        f.write(SECRET_KEY)
    del chars

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'filters': {
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.expanduser('~/error.log'),
            'maxBytes': 1024**2,
            'backupCount': 3,
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

