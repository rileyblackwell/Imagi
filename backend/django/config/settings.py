# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # Vue.js development server
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True  # Important for sending cookies

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Session settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'  # Use 'Strict' in production

# CSRF settings
CSRF_COOKIE_HTTPONLY = False  # False allows JavaScript to read the token
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_SAMESITE = 'Lax'  # Use 'Strict' in production
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

INSTALLED_APPS = [
    # ... other apps ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Should be at the top
    'django.middleware.common.CommonMiddleware',
    # ... other middleware ...
    'django.middleware.csrf.CsrfViewMiddleware',
] 