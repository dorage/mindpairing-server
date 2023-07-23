from .base import *

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', None)

ALLOWED_HOSTS = ['*', ]
# DEBUG = False
DEBUG = True
KAKAO_OAUTH_CLIENT_ID = os.environ.get('KAKAO_OAUTH_CLIENT_ID', None)
KAKAO_OAUTH_REDIRECT_URI = os.environ.get('KAKAO_OAUTH_REDIRECT_URI', None)
# "http://{HOST}/users/login/kakao/web/callback/"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
