from .base import *

DEBUG = True

TEMPLATE_DEBUG = False

SECRET_KEY = 'o15nwy&6g^-+0s)vusb&!(#4s7!v!=p+y*35yy@bi_ax9hjs6y'

MIAU_URL_BASE = 'http://localhost:5001/'

MIAU_URL_BASE_FRONTEND = 'ws://localhost:5002/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
