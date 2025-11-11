# Supabase JWT Secret Configuration

## ⚠️ Critical Security Requirement

The `SUPABASE_JWT_SECRET` is **required** for JWT signature verification. Without it, your application is vulnerable to token forgery and privilege escalation attacks.

## What is the JWT Secret?

The JWT Secret is used by Supabase to sign all authentication tokens. Your backend must use this same secret to verify that tokens are legitimate and haven't been tampered with.

## How to Find Your JWT Secret

### Method 1: Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard: https://supabase.com/dashboard
2. Select your project (`zoqyyuootjvzjlkrbqtp`)
3. Navigate to **Settings** → **API**
4. Scroll down to the **JWT Settings** section
5. Copy the **JWT Secret** value

### Method 2: Project Settings

1. Go to **Project Settings** → **API**
2. Look for **Project API keys** section
3. Find the **JWT Secret** (it's different from anon/service_role keys)
4. It should be a long string (usually 32+ characters)

## Adding to Your Environment

Add this to your `.env` file:

```bash
SUPABASE_JWT_SECRET=your-jwt-secret-here
```

**Example:**
```bash
SUPABASE_JWT_SECRET=super-secret-jwt-key-with-at-least-32-characters
```

## Security Notes

1. **Never commit** the JWT secret to Git
2. **Keep it private** - anyone with this secret can forge tokens
3. **Rotate regularly** - especially if compromised
4. **Use different secrets** for dev/staging/production

## Verification

After adding the secret, restart your backend and verify authentication works:

```bash
# Test with a real user token
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/auth/me
```

If configured correctly, you should see your user information. If the secret is wrong, you'll get a 401 Unauthorized error.

## Troubleshooting

### Error: "SUPABASE_JWT_SECRET is not configured"
- Add the secret to your `.env` file
- Restart your backend server

### Error: "Invalid token" (but token works in Supabase)
- Double-check you copied the correct JWT Secret (not anon key or service role key)
- Ensure there are no extra spaces or quotes in the `.env` file

### Error: "Token has expired"
- The token is valid but expired - user needs to log in again
- This is normal behavior for security

