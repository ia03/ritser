import os

KEYS_TO_LOAD = [
    'POSTGRES_PASSWORD',
    'SECRET_KEY',
    'GR_DEBATEFORM',
    'GR_ARGUMENTFORM',
    'GR_TOPICFORM',
    'GR_SIGNUPFORM',
    'GR_ADDEMAILFORM',
    'GR_REPORTFORM',
    'RECAPTCHA_PUBLIC',
    'RECAPTCHA_PRIVATE',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY'
]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ritser.settings")

def loading_app(wsgi_environ, start_response):
    global real_app
    import os
    for key in KEYS_TO_LOAD:
        try:
            os.environ[key] = wsgi_environ[key]
        except KeyError:
            # The WSGI environment doesn't have the key
            pass
    from django.core.wsgi import get_wsgi_application
    real_app = get_wsgi_application()
    return real_app(wsgi_environ, start_response)

real_app = loading_app

application = lambda env, start: real_app(env, start)
