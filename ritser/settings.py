"""
Django settings for udebate project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'ritser.com',
    '206.189.236.80']
INTERNAL_IPS = ['127.0.0.1', 'localhost', '209.202.207.56']



# Application definition

INSTALLED_APPS = [
    'debates.apps.DebatesConfig',
    'accounts.apps.AccountsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'haystack',
    'storages',
    'debug_toolbar',
    'reversion',
    'widget_tweaks',
    'captcha',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.reddit',
    'allauth.socialaccount.providers.google',
    'timezone_field',
    'compressor',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.UserMiddleware',
]

ROOT_URLCONF = 'ritser.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'ritser.wsgi.application'

APPEND_SLASH = True

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ritser',
                'NAME': 'postgres',
                'USER': 'postgres',
                'PASSWORD': os.environ['POSTGRES_PASSWORD'],
                'HOST': 'localhost',
                'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'accounts.User'

# Authentication backends
# https://docs.djangoproject.com/en/2.0/ref/settings/#std:setting-AUTHENTICATION_BACKENDS

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend', ]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'  # America/Toronto

USE_I18N = False

USE_L10N = False

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

if not DEBUG:
    AWS_DEFAULT_ACL = 'public-read'
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = 'ritser'
    CLOUDFRONT_DOMAIN = ''
    CLOUDFRONT_ID = 'E230MDW3NEFU7S'
    CLOUDFRONT_DOMAIN = 'd10vz1of75uuwi.cloudfront.net'
    AWS_S3_CUSTOM_DOMAIN = CLOUDFRONT_DOMAIN
    AWS_IS_GZIPPED = True
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_LOCATION = 'static'

    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'debates/static'),
    ]
    STATICFILES_STORAGE = 'debates.storage.CachedS3Boto3Storage'
    STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
    # Compressor settings
    COMPRESS_STORAGE = STATICFILES_STORAGE
    COMPRESS_URL = STATIC_URL
    COMPRESS_OFFLINE = True
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'compressor.finders.CompressorFinder',
        )
    COMPRESS_ROOT = STATIC_ROOT
    COMPRESS_URL = STATIC_URL
    COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter',  'compressor.filters.cssmin.CSSMinFilter']





# Google recaptcha settings
RECAPTCHA_REQUIRED_SCORE = 0.1

# Secret keys:
RECAPTCHA_PUBLIC_KEY = os.environ['RECAPTCHA_PUBLIC']
RECAPTCHA_PRIVATE_KEY = os.environ['RECAPTCHA_PRIVATE']

RECAPTCHA_USE_SSL = True     # Defaults to False


# Email settings

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'
DEFAULT_FROM_EMAIL = 'support@ritser.com'

# All-auth settings
SITE_ID = 4
ACCOUNT_AUTHENTICATION_METHOD = 'username'
if DEBUG:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'
else:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 1800
ACCOUNT_SIGNUP_FORM_CLASS = 'accounts.forms.SignupForm'
ACCOUNT_ADAPTER = 'accounts.adapters.DefaultAccountAdapter'
ACCOUNT_FORMS = {
    'add_email': 'accounts.forms.AddEmailForm',
}
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
#ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 300
#ACCOUNT_EMAIL_CONFIRMATION_HMAC = False

SOCIALACCOUNT_PROVIDERS = {
    'reddit': {
        'AUTH_PARAMS': {'duration': 'permanent'},
        'SCOPE': ['identity', 'submit'],
        'USER_AGENT': 'django:NIy3rZqS9dKVnQ:1.0 (by /u/fafafefefofo0)',
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Django Haystack settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# cookie settings
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# cache settings
CACHES = {
    'default': {
        'BACKEND':'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION':'127.0.0.1:11211',
    }
}

# Debug toolbar settings
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]
'''
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda r: False,  # disables it
}
'''

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
