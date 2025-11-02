# Authentication API Documentation

This document describes the authentication and profile management API endpoints for Octa Music.

## Base URL

- Development: `http://localhost:5000`
- Production: `https://octa-music.onrender.com`

## Authentication Endpoints

All authentication endpoints are prefixed with `/api/auth`.

### 1. User Registration

Register a new user account.

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "username": "string (3-30 characters, alphanumeric, underscore, dash)",
  "email": "string (valid email format)",
  "password": "string (min 8 chars, 1 uppercase, 1 number, 1 special char)",
  "confirm_password": "string (must match password)"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Registration successful! Please check your email to verify your account.",
  "data": {
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Username already exists"
}
```

**Rate Limit:** 5 requests per hour per IP

---

### 2. User Login

Authenticate user and create a session.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "login": "string (email or username)",
  "password": "string",
  "remember_me": "boolean (optional, default: false)"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Welcome back, johndoe!",
  "data": {
    "id": "user_id",
    "username": "johndoe",
    "email": "john@example.com",
    "email_verified": true,
    "created_at": "2024-01-01T12:00:00",
    "last_login": "2024-01-02T15:30:00"
  }
}
```

**Error Responses:**
- **401:** Invalid credentials
- **401:** Please verify your email address before logging in
- **429:** Too many login attempts

**Rate Limit:** 
- 3 requests per minute per IP
- 10 requests per hour per IP

---

### 3. User Logout

Log out user and clear session.

**Endpoint:** `POST /api/auth/logout` or `GET /api/auth/logout`

**Success Response (200):**
```json
{
  "success": true,
  "message": "You have been logged out successfully."
}
```

---

### 4. Email Verification

Verify user email with token from verification email.

**Endpoint:** `GET /api/auth/verify-email/<token>`

**Response:** Renders HTML page with verification result

**Success:** Shows "Email verified successfully! You can now log in."

**Error:** Shows "Invalid or expired verification link."

---

### 5. Request Password Reset

Request a password reset email.

**Endpoint:** `POST /api/auth/reset-request`

**Request Body:**
```json
{
  "email": "string"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "If the email exists, a reset link has been sent."
}
```

**Note:** For security, always returns generic success message regardless of whether email exists.

**Rate Limit:** 3 requests per hour per IP

---

### 6. Reset Password

Reset password using token from reset email.

**Endpoint:** `POST /api/auth/reset-password/<token>`

**Request Body:**
```json
{
  "password": "string (min 8 chars, 1 uppercase, 1 number, 1 special char)",
  "confirm_password": "string (must match password)"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Password changed successfully. Please login."
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Invalid or expired reset link"
}
```

---

### 7. Session Check

Check if current session is valid.

**Endpoint:** `GET /api/auth/session-check`

**Success Response (200) - Authenticated:**
```json
{
  "success": true,
  "authenticated": true,
  "data": {
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

**Success Response (200) - Not Authenticated:**
```json
{
  "success": true,
  "authenticated": false
}
```

---

### 8. Refresh Session

Refresh session to extend timeout (only works with remember_me enabled).

**Endpoint:** `POST /api/auth/refresh-session`

**Success Response (200):**
```json
{
  "success": true,
  "message": "Session refreshed"
}
```

**Error Responses:**
- **401:** No active session
- **403:** Session refresh not available (remember_me not enabled)

---

## Profile Management Endpoints

All profile endpoints are prefixed with `/api/profile` and require authentication.

### 1. Get Profile

Get current user's profile information.

**Endpoint:** `GET /api/profile/`

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "user_id",
    "username": "johndoe",
    "email": "john@example.com",
    "email_verified": true,
    "created_at": "2024-01-01T12:00:00",
    "last_login": "2024-01-02T15:30:00"
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "message": "Authentication required"
}
```

---

### 2. Update Username

Update user's username.

**Endpoint:** `PUT /api/profile/username`

**Request Body:**
```json
{
  "username": "string (3-30 characters)"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Username updated successfully"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Username already exists"
}
```

---

### 3. Update Email

Update user's email (requires re-verification).

**Endpoint:** `PUT /api/profile/email`

**Request Body:**
```json
{
  "email": "string (valid email)"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Email updated. Please check your new email to verify it."
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Email already exists"
}
```

---

### 4. Change Password

Change user's password.

**Endpoint:** `PUT /api/profile/password`

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string (min 8 chars, 1 uppercase, 1 number, 1 special char)",
  "confirm_password": "string (must match new_password)"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Error Responses:**
- **400:** Current password is incorrect
- **400:** Password validation failed

---

## Password Requirements

All password fields must meet the following requirements:

- **Minimum length:** 8 characters
- **Uppercase:** At least 1 uppercase letter (A-Z)
- **Lowercase:** At least 1 lowercase letter (a-z)
- **Number:** At least 1 digit (0-9)
- **Special character:** At least 1 special character (!@#$%^&*(),.?":{}|<>_-+=[]\\;/\`~)

---

## Session Management

### Session Duration

- **Default session:** 80 minutes of inactivity
- **Remember me session:** 30 days
- **Session warning:** Shown at 70 minutes (10 minutes before expiration)

### Session Storage

Sessions are stored in secure, HTTPOnly cookies with the following data:
- `user_id`: User ID
- `username`: Username
- `email`: Email address
- `remember_me`: Boolean flag

### Security Features

- **HTTPOnly cookies:** Prevents XSS attacks
- **SameSite=Lax:** Prevents CSRF attacks
- **Secure flag:** HTTPS only in production
- **Session timeout:** Automatic expiration

---

## Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request - Invalid input |
| 401  | Unauthorized - Authentication required |
| 403  | Forbidden - Insufficient permissions |
| 404  | Not Found |
| 429  | Too Many Requests - Rate limit exceeded |
| 500  | Internal Server Error |

---

## Rate Limiting

Rate limits are enforced per IP address:

| Endpoint | Limit |
|----------|-------|
| Registration | 5 per hour |
| Login | 3 per minute, 10 per hour |
| Password Reset Request | 3 per hour |
| All other endpoints | 200 per day, 50 per hour |

When rate limit is exceeded, the API returns a 429 status code with message:
```json
{
  "success": false,
  "message": "Too many requests. Please try again later."
}
```

---

## Security Considerations

### Password Hashing

- Passwords are hashed using **bcrypt** with 12 salt rounds
- Plain text passwords are never stored
- Password hashes are never exposed in API responses

### Token Security

- Email verification tokens expire after **24 hours**
- Password reset tokens expire after **1 hour**
- Tokens are one-time use and invalidated after successful use
- Tokens are generated using `itsdangerous.URLSafeTimedSerializer`

### Account Lockout

- After **5 failed login attempts**, account is locked for **15 minutes**
- Lockout is automatically cleared after timeout period

### HTTPS

- In production, all authentication endpoints require HTTPS
- Session cookies have the `Secure` flag set in production

---

## Development Mode

In development mode (`APP_ENV=development`):

- Emails are printed to console instead of being sent
- `MAIL_SUPPRESS_SEND=True` by default
- Session cookies allow HTTP (no `Secure` flag)

To view verification/reset links in development, check the console output:
```
[DEV MODE] Email verification link for user@example.com: http://localhost:5000/api/auth/verify-email/token123
```

---

## Example Usage

### Complete Registration Flow

1. **Register user:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
  }'
```

2. **Check console for verification link** (dev mode)

3. **Verify email:**
```bash
curl http://localhost:5000/api/auth/verify-email/TOKEN_FROM_EMAIL
```

4. **Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "johndoe",
    "password": "SecurePass123!",
    "remember_me": true
  }' \
  -c cookies.txt
```

5. **Access profile:**
```bash
curl http://localhost:5000/api/profile/ \
  -b cookies.txt
```

---

## Support

For issues or questions about the authentication API, please contact the development team or create an issue in the GitHub repository.
