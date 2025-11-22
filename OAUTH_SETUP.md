# OAuth Setup Guide for SmartFixer

This guide will help you set up Google and GitHub OAuth authentication.

## Prerequisites

1. A Google account
2. A GitHub account
3. Access to Google Cloud Console
4. Access to GitHub Developer Settings

## Step 1: Set Up Google OAuth

### 1.1 Create OAuth Credentials in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth client ID**
5. If prompted, configure the OAuth consent screen:
   - Choose **External** user type
   - Fill in the required information (App name, User support email, Developer contact)
   - Add scopes: `openid`, `profile`, `email`
   - Add test users if needed
6. For Application type, select **Web application**
7. Add Authorized redirect URIs:
   - `http://localhost:5000/auth/google/callback` (for local development)
   - `http://127.0.0.1:5000/auth/google/callback` (alternative local)
   - `https://yourdomain.com/auth/google/callback` (for production)
8. Click **Create**
9. Copy the **Client ID** and **Client Secret**

### 1.2 Add to .env File

Create or edit a `.env` file in your project root:

```env
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here
```

## Step 2: Set Up GitHub OAuth

### 2.1 Create OAuth App in GitHub

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **OAuth Apps** > **New OAuth App**
3. Fill in the application details:
   - **Application name**: SmartFixer (or your app name)
   - **Homepage URL**: `http://localhost:5000` (for local) or your production URL
   - **Authorization callback URL**: 
     - `http://localhost:5000/auth/github/callback` (for local)
     - `https://yourdomain.com/auth/github/callback` (for production)
4. Click **Register application**
5. Copy the **Client ID**
6. Click **Generate a new client secret** and copy the **Client Secret**

### 2.2 Add to .env File

Add to your `.env` file:

```env
GITHUB_OAUTH_CLIENT_ID=your_github_client_id_here
GITHUB_OAUTH_CLIENT_SECRET=your_github_client_secret_here
```

## Step 3: Complete .env File

Your complete `.env` file should look like this:

```env
# OAuth Credentials
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here
GITHUB_OAUTH_CLIENT_ID=your_github_client_id_here
GITHUB_OAUTH_CLIENT_SECRET=your_github_client_secret_here

# Other environment variables
SESSION_SECRET=your-secret-key-here
DATABASE_URL=sqlite:///app.db
```

## Step 4: Restart Your Server

After adding the credentials, restart your Flask server:

```bash
python app.py
```

You should see:
- `✅ Google OAuth configured successfully`
- `✅ GitHub OAuth configured successfully`

If you see warnings, check that:
1. The credentials are correct
2. The redirect URIs match exactly
3. The .env file is in the project root

## Troubleshooting

### Error: "OAuth client was not found" (Google)

- Check that the Client ID is correct
- Verify the redirect URI matches exactly (including http/https and port)
- Make sure the OAuth consent screen is configured
- Check that the project is active in Google Cloud Console

### Error: "redirect_uri_mismatch" (Google)

- The redirect URI in your code must match exactly with what's in Google Cloud Console
- Check for trailing slashes, http vs https, and port numbers
- Current redirect URI: `http://localhost:5000/auth/google/callback`

### GitHub OAuth Not Working

- Verify the callback URL matches exactly
- Check that the Client ID and Secret are correct
- Make sure the OAuth app is not suspended

### Both OAuth Not Working

- Check that the `.env` file exists in the project root
- Verify environment variables are loaded (restart server)
- Check server console for error messages

## Testing

1. Go to `http://localhost:5000/auth`
2. Click "Continue with Google" or "Continue with GitHub"
3. You should be redirected to the OAuth provider
4. After authorization, you should be redirected back and logged in

## Production Deployment

For production, update the redirect URIs in both:
- Google Cloud Console
- GitHub OAuth App settings

Use your production domain instead of localhost.

