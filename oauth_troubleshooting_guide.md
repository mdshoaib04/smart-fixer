# Google OAuth Troubleshooting Guide

## Current Status
✅ OAuth credentials are properly configured
✅ Custom redirect URI fix is implemented
✅ Application is using real Google OAuth credentials

## Common Issues and Solutions

### 1. Application Restart Required
After making changes to the code or configuration, you must completely restart the application:

```bash
# Stop the current application (Ctrl+C)
# Start it again
python app.py
```

### 2. Verify Google Cloud Console Configuration
Double-check that you've added the exact redirect URI in Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" → "Credentials"
3. Click on your OAuth 2.0 Client ID
4. Verify that `http://localhost:5000/callback/google` is in "Authorized redirect URIs"
5. Make sure there are no extra spaces or characters
6. Click "Save" to ensure changes are applied

### 3. Try Alternative Redirect URIs
If the standard localhost URI doesn't work, try these alternatives:
- `http://127.0.0.1:5000/callback/google`
- `http://localhost/callback/google` (if running on port 80)

### 4. Check Browser Console for Detailed Errors
Open your browser's developer tools (F12) and check the Console tab for any error messages when clicking "Sign up with Google".

### 5. Check Application Terminal for Errors
Look at the terminal where you started the application for any error messages during the OAuth flow.

### 6. Clear Browser Cache and Cookies
Sometimes cached data can cause issues:
1. Clear your browser cache and cookies
2. Try opening the application in an incognito/private window

### 7. Verify You're Accessing the Correct URL
Make sure you're accessing the application at:
- `http://localhost:5000`
- NOT `http://127.0.0.1:5000` (unless you specifically configured this)

### 8. Create a New OAuth Client (Last Resort)
If all else fails:
1. In Google Cloud Console, create a new OAuth 2.0 Client ID
2. Add the redirect URIs again
3. Update your `.env` file with the new credentials
4. Restart the application

## Testing the OAuth Flow
To test if the OAuth flow is working correctly:

1. Start the application: `python app.py`
2. Open your browser and go to `http://localhost:5000`
3. Click on "Continue with Google" button
4. You should be redirected to Google's authentication page
5. After authenticating, you should be redirected back to your application

## Debug Information
- Application Port: 5000
- Expected Redirect URI: `http://localhost:5000/callback/google`
- Google Client ID Format: ✅ Valid (ends with .apps.googleusercontent.com)

## Need More Help?
If you're still experiencing issues:

1. Take a screenshot of:
   - The exact error message you're seeing
   - Your Google Cloud Console OAuth client configuration
   - Your browser's developer console when the error occurs

2. Check the application terminal for any error messages during the OAuth flow

3. Verify that all the fixes we've implemented are present in your code