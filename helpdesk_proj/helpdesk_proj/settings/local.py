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
