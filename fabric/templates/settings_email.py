EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "{{host}}"
EMAIL_HOST_USER = "{{address}}"
EMAIL_HOST_PASSWORD = "{{password}}"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL="{{address}}"
