# Quick Start: Google SSO

## 🚀 5-Minute Setup

### 1. Get Google Credentials (2 min)
1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth client ID (Web application)
3. Add redirect URI: `http://localhost:5174/api/accounts/google/login/callback/`
4. Copy Client ID and Secret

### 2. Configure Backend (1 min)
Add to `backend/django/.env`:
```bash
GOOGLE_OAUTH_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_secret
```

### 3. Run Migration (1 min)
```bash
cd backend/django
python manage.py migrate
```

### 4. Test (1 min)
1. Register a user with email
2. Click "Continue with Google" on login
3. Sign in with same email
4. ✅ Success!

## Production Setup

### Railway Environment Variables
```
GOOGLE_OAUTH_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_secret
```

### Production Redirect URI
```
https://imagi.up.railway.app/api/accounts/google/login/callback/
```

## How It Works

```
User clicks "Continue with Google"
    ↓
Google OAuth consent screen
    ↓
User authorizes
    ↓
Backend checks if email exists
    ↓
If exists: Login success ✅
If not: Show error message ❌
```

## Key Features

- ✅ Existing-email-only (no auto-signup)
- ✅ Secure token-based auth
- ✅ Beautiful UI integration
- ✅ Error handling
- ✅ Production-ready

## Need More Details?

- Full setup: `GOOGLE_SSO_SETUP.md`
- Implementation: `../../../GOOGLE_SSO_IMPLEMENTATION.md`
- Activation checklist: `../../../GOOGLE_SSO_ACTIVATION_CHECKLIST.md`
