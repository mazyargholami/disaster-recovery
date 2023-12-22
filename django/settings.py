MIDDLEWARE = [
    # ...
    'path.to.your.middleware.DatabaseFallbackMiddleware',
    # ...
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'primary_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'fallback': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fallback_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
}
