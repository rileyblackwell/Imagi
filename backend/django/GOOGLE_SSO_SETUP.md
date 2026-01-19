# Google SSO Setup Guide

This guide explains how to configure Google OAuth for the Imagi application.

## Overview

The application uses Django Allauth with Google OAuth provider to enable users to sign in with their Google accounts. The implementation enforces an **existing-email-only** policy, meaning users can only sign in with Google if they already have an account with that email address.

## Prerequisites

- Google Cloud Console account
- Access to the Imagi backend environment variables

## Google Cloud Console Configuration

### 1. Create OAuth 2.0 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth client ID**
5. Select **Web application** as the application type
6. Configure the OAuth client:

### 2. Set Authorized JavaScript Origins

Add the following origins:

**Local Development:**
```
http://localhost:5174
```

**Railway Production:**
```
https://imagi.up.railway.app
```

### 3. Set Authorized Redirect URIs

Add the following redirect URIs:

**Local Development:**
```
http://localhost:5174/api/accounts/google/login/callback/
```

**Railway Production:**
```
https://imagi.up.railway.app/api/accounts/google/login/callback/
```

### 4. Save and Get Credentials

After creating the OAuth client, you'll receive:
- **Client ID** (starts with something like `123456789-abc...apps.googleusercontent.com`)
- **Client Secret** (a random string)

## Backend Environment Configuration

Add the following environment variables to your Django backend:

### Local Development (.env file)

```bash
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
```

### Railway Production

Add these environment variables in the Railway dashboard:

1. Go to your backend service in Railway
2. Navigate to **Variables** tab
3. Add:
   - `GOOGLE_OAUTH_CLIENT_ID`: Your Google OAuth Client ID
   - `GOOGLE_OAUTH_CLIENT_SECRET`: Your Google OAuth Client Secret

## Database Migration

After configuring the settings, run migrations to create the necessary social account tables:

```bash
cd backend/django
python manage.py migrate
```

This will create tables for:
- `socialaccount_socialaccount`
- `socialaccount_socialapp`
- `socialaccount_socialtoken`

## How It Works

### Authentication Flow

1. User clicks "Continue with Google" on the login page
2. Frontend redirects to `/api/v1/auth/google/start/`
3. Backend redirects to Google OAuth consent screen
4. User authorizes the application
5. Google redirects back to `/api/accounts/google/login/callback/`
6. Django Allauth processes the OAuth callback
7. `CustomSocialAccountAdapter` checks if user email exists:
   - **If exists**: Connects Google account to user, redirects to `/api/v1/auth/google/complete/`
   - **If not exists**: Redirects to login page with error `?sso_error=no_account`
8. Complete endpoint mints DRF Token and redirects to frontend callback
9. Frontend stores token and redirects user to dashboard

### Security Features

- **Existing-email-only policy**: Users must register with email/password first
- **Email verification**: Only verified Google emails are accepted
- **Token-based auth**: Uses existing DRF Token authentication
- **CSRF protection**: All endpoints are CSRF-protected
- **CORS configured**: Proper CORS headers for Railway architecture

## Testing

### Local Testing

1. Start the Django backend:
   ```bash
   cd backend/django
   python manage.py runserver
   ```

2. Start the Vue frontend:
   ```bash
   cd frontend/vuejs
   npm run dev
   ```

3. Create a test user with email/password
4. Try signing in with Google using the same email
5. Verify successful authentication

### Production Testing

1. Deploy to Railway
2. Ensure environment variables are set
3. Test the OAuth flow end-to-end
4. Verify error handling for non-existing emails

## Troubleshooting

### Common Issues

**"redirect_uri_mismatch" error:**
- Verify the redirect URI in Google Console exactly matches the one in the error message
- Ensure no trailing slashes mismatch
- Check that you're using the correct domain (localhost vs Railway)

**"no_account" error:**
- User must first register with email/password
- The email used for registration must match the Google account email

**"no_email" error:**
- Google account doesn't have a verified email
- User should verify their email in Google account settings

**Token not working:**
- Check that FRONTEND_URL is correctly set in Django settings
- Verify CORS settings allow the frontend origin
- Check browser console for errors

## Additional Configuration

### Customizing Scopes

To request additional Google profile information, edit `settings.py`:

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
            # Add more scopes as needed
        ],
        ...
    }
}
```

### Customizing Error Messages

Edit `apps/Auth/social_adapters.py` to customize error handling and redirect behavior.

### Frontend Customization

Edit `frontend/vuejs/src/apps/auth/views/Login.vue` to customize the Google button appearance and behavior.

## Support

For issues or questions:
1. Check Django logs for backend errors
2. Check browser console for frontend errors
3. Verify all environment variables are set correctly
4. Ensure Google Cloud Console configuration matches this guide
