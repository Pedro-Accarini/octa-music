# Agent Prompt: Implement Complete Login/Authentication System for Octa Music

## 🎯 Objective
Implement a complete, production-ready authentication system for the Octa Music Flask application with user registration, login, logout, profile management, password reset, and email verification.

---

## 📋 Project Context

### Current Tech Stack
- **Backend**: Flask (Python)
- **Database**: MongoDB (to be set up - MongoDB Atlas free tier)
- **Frontend**: HTML templates with existing design system
- **Current Dependencies**: Flask, spotipy, python-dotenv, pytest, gunicorn, flask-cors, flask-limiter
- **Existing Design**: Design tokens system (`design-tokens.css`, `base.css`, `main.css`)
- **Existing Toast System**: Already implemented in `main.html`

### Current Project Structure
```
src/
├── __init__.py
├── api/
│   ├── __init__.py
│   └── routes.py
├── config.py
├── main.py
├── models.py
├── services/
│   ├── spotify_service.py
│   └── youtube_service.py
├── static/
│   └── css/
│       ├── design-tokens.css
│       ├── base.css
│       ├── main.css
│       ├── playlists.css
│       ├── spotify.css
│       └── youtube.css
├── templates/
│   ├── main.html (base template with navbar and toast system)
│   ├── spotify.html
│   ├── youtube.html
│   └── [other templates]
└── version.py
```

---

## 🔐 Authentication Requirements

### 1. Authentication Strategy
- **Type**: Local authentication only (username/email + password)
- **Storage**: MongoDB database (users collection)
- **Session**: Cookie-based sessions (Flask sessions)
- **No OAuth** for now (placeholders only for future social login)

### 2. User Registration

#### Registration Fields
- **Username**: Required, unique, 3-30 characters
- **Email**: Required, unique, valid email format
- **Password**: Required with complexity rules:
  - Minimum 8 characters
  - At least 1 uppercase letter
  - At least 1 number
  - At least 1 special character

#### Registration Flow
1. User fills registration form
2. Validate all fields (client-side + server-side)
3. Check if email/username already exists
4. Hash password using **bcrypt**
5. Create user record in MongoDB
6. Send verification email
7. Show success message: "Registration successful! Please check your email to verify your account."
8. Redirect to login page

#### Email Verification
- Send verification email with unique token
- Token expires after 24 hours
- User must verify email before login
- Endpoint: `/api/auth/verify-email/<token>`

### 3. User Login

#### Login Flow
1. User enters email/username and password
2. Server validates credentials
3. Check if email is verified
4. If valid, create session (80-minute timeout)
5. Support "Remember Me" checkbox (30 days if checked)
6. Redirect to home page with welcome toast
7. Update navbar to show logged-in state

#### Rate Limiting
- **3 failed attempts per minute** per IP/user
- **10 failed attempts per hour** per IP/user
- After exceeding limits, show: "Too many login attempts. Please try again later."
- Use Flask-Limiter for implementation

#### Error Messages
- **Generic for security**: "Invalid credentials" (don't reveal if email exists)
- Unverified email: "Please verify your email address before logging in."

### 4. Session Management

#### Session Configuration
- **Session Timeout**: 80 minutes of inactivity
- **Remember Me**: 30 days persistent session
- **Multi-device**: Allowed (multiple sessions per user)
- **Session Warning**: Show toast at **70 minutes** (10 min before timeout): "Your session will expire in 10 minutes."
- **No extend button**: User must re-login after timeout

#### Session Storage
- Use Flask secure sessions with cookies
- Store: `user_id`, `username`, `email`, `login_time`, `remember_me`
- HTTPS enforcement in production

### 5. Password Reset

#### Reset Flow
1. User clicks "Forgot Password?" on login page
2. Enter email address
3. Server sends reset email (if email exists)
4. **Generic message**: "If the email exists, a reset link has been sent." (security)
5. Reset link valid for 1 hour
6. User clicks link, enters new password
7. Password validated against complexity rules
8. Password updated, all other sessions invalidated
9. Success message, redirect to login

### 6. User Profile/Settings Page

#### Profile Page (`/profile`)
- **Accessible**: Only when logged in (redirect to login if not)
- **Display**:
  - Username
  - Email
  - Account created date
  - Last login timestamp

#### Edit Functionality
- **Edit Username**: Update with validation (unique, 3-30 chars)
- **Edit Email**: Update with new verification email sent
- **Change Password**: Require current password, validate new password
- **No delete account option**

#### Search History (Backend Only - Not Displayed)
- Track all Spotify searches for logged-in users
- Store in MongoDB (separate collection `search_history` or embedded in user document)
- Fields: `user_id`, `search_query`, `timestamp`, `results` (artist IDs/names)
- Automatically saved on each search
- Not displayed in UI (for now, future feature)

---

## 🗄️ Database Design

### MongoDB Configuration
- **Service**: MongoDB Atlas (free tier)
- **Connection**: Store URI in GitHub Secrets (`MONGODB_URI`) and `.env` for local dev
- **Database Name**: `octa_music`
- **Collections**:

#### Collection: `users`
```json
{
  "_id": ObjectId,
  "username": String (unique, indexed),
  "email": String (unique, indexed),
  "password_hash": String (bcrypt),
  "email_verified": Boolean (default: false),
  "verification_token": String (nullable),
  "verification_token_expires": DateTime (nullable),
  "reset_token": String (nullable),
  "reset_token_expires": DateTime (nullable),
  "created_at": DateTime,
  "last_login": DateTime (nullable),
  "failed_login_attempts": Integer (default: 0),
  "lockout_until": DateTime (nullable)
}
```

#### Collection: `search_history` (or embedded array in users)
```json
{
  "_id": ObjectId,
  "user_id": ObjectId (reference to users),
  "search_query": String,
  "timestamp": DateTime,
  "results": Array (artist names/IDs)
}
```

---

## 🎨 UI/UX Design Requirements

### Design System Integration
- **MUST use existing design tokens** from `design-tokens.css`
- **Match existing UI patterns** in current templates
- **Responsive**: Use same breakpoints as current site (320px, 375px, 412px, 480px, 768px, 1024px, 1280px, 1440px)
- **Dark mode support**: Full compatibility with existing dark mode toggle
- **Accessibility**: WCAG AA compliance

### Page Layouts

#### Login Page (`/login`)
- **Separate page** (not modal)
- Form fields:
  - Email or Username (input)
  - Password (input with show/hide toggle)
  - Remember Me (checkbox)
  - Submit button: "Login"
- Links:
  - "Forgot Password?"
  - "Don't have an account? Register"
- Social login placeholder buttons (non-functional):
  - "Continue with Google" (disabled/greyed out)
  - "Continue with Spotify" (disabled/greyed out)
  - "Continue with GitHub" (disabled/greyed out)
  - Add tooltip: "Coming soon"

#### Registration Page (`/register`)
- **Separate page** (not modal)
- Form fields:
  - Username (input)
  - Email (input)
  - Password (input with show/hide toggle, strength indicator)
  - Confirm Password (input)
  - Submit button: "Create Account"
- Link: "Already have an account? Login"
- Same social login placeholders as login page

#### Password Reset Pages
- **Request Reset** (`/reset-password`):
  - Email input
  - Submit button: "Send Reset Link"
  - Link back to login
  
- **Reset Password** (`/reset-password/<token>`):
  - New password input (with strength indicator)
  - Confirm password input
  - Submit button: "Reset Password"

#### Profile Page (`/profile`)
- Card-based layout matching existing design
- Display sections:
  - User info (username, email, created date, last login)
  - Edit username (inline edit or modal)
  - Edit email (inline edit or modal)
  - Change password (separate form)

### Navbar Updates

#### When Logged Out
- **Hamburger menu** (mobile): Add "Login" and "Register" links
- **Desktop nav**: Add "Login" and "Register" buttons on the right side

#### When Logged In
- **Hamburger menu**: Add "Profile" and "Logout" links
- **Desktop nav**: Add user dropdown on right side:
  - Display: Username or avatar icon
  - Dropdown items:
    - Profile
    - Logout
- **Both places**: Logout functionality must be available

### Toast Notifications
- **Use existing toast system** in `main.html`
- Toast types to implement:
  - `success`: Green, for successful actions
  - `error`: Red, for errors
  - `warning`: Yellow/orange, for session warnings
  - `info`: Blue, for informational messages

#### Toast Messages
- Login success: "Welcome back, {username}!"
- Logout: "You have been logged out successfully."
- Registration success: "Registration successful! Please check your email."
- Password reset sent: "If the email exists, a reset link has been sent."
- Password reset success: "Password changed successfully. Please login."
- Session warning (70 min): "Your session will expire in 10 minutes."
- Session expired: "Your session has expired. Please login again."
- Profile updated: "Profile updated successfully."
- Email verification: "Email verified successfully!"

---

## 🛠️ Technical Implementation

### File Structure to Create

```
src/
├── api/
│   └── auth_routes.py          # NEW: Authentication API endpoints
├── models/
│   └── user_model.py            # NEW: User model for MongoDB
├── services/
│   ├── auth_service.py          # NEW: Authentication business logic
│   ├── database_service.py      # NEW: MongoDB connection and utilities
│   └── email_service.py         # NEW: Email sending functionality
├── static/
│   ├── css/
│   │   └── auth.css             # NEW: Authentication pages styling
│   └── js/
│       ├── auth.js              # NEW: Login/register form validation
│       ├── session.js           # NEW: Session timeout management
│       └── profile.js           # NEW: Profile page interactions
├── templates/
│   └── auth/
│       ├── login.html           # NEW: Login page
│       ├── register.html        # NEW: Registration page
│       ├── reset_request.html   # NEW: Request password reset
│       ├── reset_password.html  # NEW: Reset password form
│       ├── verify_email.html    # NEW: Email verification page
│       └── profile.html         # NEW: User profile page
└── utils/
    └── validators.py            # NEW: Input validation utilities
```

### Dependencies to Add

Update `requirements.txt`:
```
Flask
spotipy
python-dotenv
pytest
gunicorn
flask-cors
flask-limiter
pymongo                  # MongoDB driver
flask-pymongo            # Flask-MongoDB integration
bcrypt                   # Password hashing
flask-login              # Session management
flask-mail               # Email sending
itsdangerous             # Token generation
email-validator          # Email validation
```

### API Endpoints to Create

#### Authentication Endpoints (`/api/auth/*`)
```python
POST   /api/auth/register          # User registration
POST   /api/auth/login             # User login
POST   /api/auth/logout            # User logout
GET    /api/auth/verify-email/<token>  # Email verification
POST   /api/auth/reset-request     # Request password reset
POST   /api/auth/reset-password/<token>  # Reset password
GET    /api/auth/session-check     # Check session validity
POST   /api/auth/refresh-session   # Refresh session (for remember me)
```

#### Profile Endpoints (`/api/profile/*`)
```python
GET    /api/profile                # Get user profile
PUT    /api/profile/username       # Update username
PUT    /api/profile/email          # Update email
PUT    /api/profile/password       # Change password
```

#### All endpoints return JSON:
```json
{
  "success": true/false,
  "message": "Human-readable message",
  "data": {}  // Optional payload
}
```

### Configuration Updates

#### `.env.example` (CREATE THIS FILE)
```env
# Flask Configuration
FLASK_APP=src.main
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# MongoDB Configuration
MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/octa_music?retryWrites=true&w=majority

# Email Configuration (Gmail SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Email Configuration (Outlook SMTP - Alternative)
# MAIL_SERVER=smtp-mail.outlook.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=your-email@outlook.com
# MAIL_PASSWORD=your-password
# MAIL_DEFAULT_SENDER=your-email@outlook.com

# Session Configuration
SESSION_COOKIE_SECURE=False  # Set to True in production (HTTPS only)
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=4800  # 80 minutes in seconds
REMEMBER_ME_DURATION=2592000     # 30 days in seconds

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
LOGIN_RATE_LIMIT_PER_MINUTE=3
LOGIN_RATE_LIMIT_PER_HOUR=10

# Application URLs
FRONTEND_URL=http://localhost:5000  # Change in production
```

#### GitHub Secrets to Configure (Document in README)
```
MONGODB_URI
SECRET_KEY
MAIL_USERNAME
MAIL_PASSWORD
```

#### Update `src/config.py`
Add configuration classes for different environments (development, production) that read from environment variables.

---

## 🔒 Security Requirements

### Password Security
- **Hashing**: Use bcrypt with salt rounds = 12
- **Never store plain text passwords**
- **Password validation**: Client-side and server-side

### Session Security
- **Secure cookies**: HTTPOnly, SameSite=Lax
- **HTTPS only in production**: `SESSION_COOKIE_SECURE=True`
- **CSRF protection**: Implement CSRF tokens for all forms
- **Session invalidation**: On logout, password change, email change

### Email Security
- **Token-based verification**: Use `itsdangerous` for secure tokens
- **Token expiration**: 
  - Email verification: 24 hours
  - Password reset: 1 hour
- **One-time use tokens**: Invalidate after use

### Rate Limiting
- **Login attempts**: 3 per minute, 10 per hour (per IP + per user)
- **Registration**: 5 per hour per IP
- **Password reset requests**: 3 per hour per IP
- **Email verification resend**: 3 per hour per user

### Input Validation
- **Server-side validation**: Never trust client input
- **Sanitize all inputs**: Prevent XSS, SQL injection (though using MongoDB)
- **Email validation**: Use `email-validator` library
- **Username validation**: Alphanumeric + underscore/dash only

### HTTPS Enforcement
- **Production only**: Redirect HTTP to HTTPS
- **Development**: Allow HTTP for local testing

---

## 🧪 Testing Requirements

### Unit Tests (`tests/test_auth.py`)
- User model CRUD operations
- Password hashing and verification
- Token generation and validation
- Email validation
- Username validation
- Password complexity validation

### Integration Tests (`tests/test_auth_integration.py`)
- Complete registration flow
- Complete login flow
- Email verification flow
- Password reset flow
- Session management
- Rate limiting enforcement
- Profile update operations

### Test Coverage
- Aim for **>80% code coverage** for authentication code
- Test error cases and edge cases
- Test with valid and invalid inputs

### Test Data
- Create fixtures for test users
- Mock email sending in tests
- Use test MongoDB database (separate from dev/prod)

---

## 📝 Documentation Requirements

### README.md Updates
Add new section: "Authentication System Setup"

Include:
1. **MongoDB Atlas Setup Instructions**:
   - Create free account
   - Create cluster
   - Create database user
   - Get connection string
   - Configure IP whitelist

2. **Email Configuration**:
   - Gmail: Enable 2FA, generate app-specific password
   - Outlook: Configure SMTP access
   - Add credentials to `.env`

3. **Environment Variables**:
   - Copy `.env.example` to `.env`
   - Fill in all required values
   - Instructions for each variable

4. **Local Development**:
   - How to run with authentication
   - Test user creation
   - Email testing (print to console in dev mode)

5. **GitHub Secrets Configuration**:
   - List of required secrets
   - How to add them in repository settings
   - Production vs development differences

### API Documentation
Create `API_AUTHENTICATION.md`:
- Document all authentication endpoints
- Request/response examples
- Error codes and messages
- Authentication flow diagrams

### Code Comments
- Clear docstrings for all functions
- Explain complex logic
- Security considerations noted in comments

---

## ✅ Acceptance Criteria

### Functionality Checklist
- [ ] User can register with email, username, password
- [ ] Email verification required before login
- [ ] User can login with email/username and password
- [ ] "Remember me" keeps user logged in for 30 days
- [ ] Rate limiting prevents brute force attacks
- [ ] User can reset password via email
- [ ] User can view profile (username, email, dates)
- [ ] User can edit username, email, password
- [ ] Session expires after 80 minutes
- [ ] Warning shown at 70 minutes
- [ ] User can logout from navbar (desktop + mobile)
- [ ] Navbar shows login status correctly
- [ ] Search history saved for logged-in users (backend only)
- [ ] All forms have client-side and server-side validation
- [ ] Toast notifications work for all actions
- [ ] Social login buttons visible but disabled (placeholders)

### Design Checklist
- [ ] All pages match existing design system
- [ ] Dark mode works on all auth pages
- [ ] Responsive design works on all breakpoints
- [ ] Forms are accessible (WCAG AA)
- [ ] Error messages are clear and helpful
- [ ] Loading states for async operations
- [ ] Password strength indicator on registration/reset

### Security Checklist
- [ ] Passwords hashed with bcrypt
- [ ] Sessions secured with HTTPOnly cookies
- [ ] CSRF protection implemented
- [ ] Rate limiting active on all auth endpoints
- [ ] Email tokens expire appropriately
- [ ] No sensitive data in URLs or logs
- [ ] HTTPS enforced in production
- [ ] Input validation prevents injection attacks

### Code Quality Checklist
- [ ] Code follows existing project patterns
- [ ] Clear separation of concerns (routes, services, models)
- [ ] Error handling comprehensive
- [ ] Logging for security events
- [ ] Tests pass with >80% coverage
- [ ] No hardcoded secrets or credentials
- [ ] Documentation complete and accurate
- [ ] Type hints used where applicable

### Integration Checklist
- [ ] MongoDB connection working
- [ ] Email sending working (Gmail and Outlook)
- [ ] Existing Spotify search still works
- [ ] No breaking changes to existing features
- [ ] Environment variables properly configured
- [ ] GitHub Secrets documented
- [ ] Production deployment ready

---

## 🚀 Implementation Notes

### Development Approach
1. **Phase 1**: Database setup and models
2. **Phase 2**: Core authentication (register, login, logout)
3. **Phase 3**: Email verification and password reset
4. **Phase 4**: Profile management
5. **Phase 5**: Session management and rate limiting
6. **Phase 6**: UI/UX polish and responsive design
7. **Phase 7**: Testing and documentation
8. **Phase 8**: Integration with search history tracking

### Error Handling Strategy
- **User-facing errors**: Clear, helpful messages via toast
- **Server errors**: Log detailed info, show generic message to user
- **Validation errors**: Specific field-level feedback
- **Security errors**: Generic messages to prevent information leakage

### Email Configuration Priority
1. Try Gmail SMTP first (more common)
2. Fallback to Outlook SMTP
3. Document both in `.env.example`
4. Log email sending errors
5. In development: Print email content to console instead of sending

### Session Warning Implementation
- JavaScript timer starts on page load if authenticated
- Check session age from server
- Show toast at 70 minutes (10 min before expiry)
- Poll server every 5 minutes to check session validity
- Auto-logout and redirect if session expired

### Search History Integration
- Modify existing Spotify search route
- After successful search, if user logged in, save to `search_history`
- Don't break existing functionality for non-logged-in users
- Store minimal data: query, timestamp, top 5 results

---

## 🎯 Success Metrics
- [ ] All acceptance criteria met
- [ ] All tests passing
- [ ] Code review approved
- [ ] Documentation complete
- [ ] No security vulnerabilities
- [ ] Performance acceptable (<500ms response time for auth operations)
- [ ] Works in development and production environments

---

## 📌 Important Reminders for Agent

1. **DO NOT break existing functionality** - Spotify/YouTube search must continue to work
2. **FOLLOW existing design patterns** - Match current CSS/HTML structure
3. **USE existing toast system** - Don't create a new one
4. **RESPECT the design tokens** - Don't introduce new colors/spacing
5. **TEST thoroughly** - Both automated and manual testing
6. **DOCUMENT everything** - Future developers need to understand this
7. **SECURE by default** - Security is not optional
8. **MOBILE FIRST** - Test on all breakpoints
9. **ACCESSIBILITY matters** - WCAG AA compliance required
10. **NO hardcoded secrets** - Everything in env vars

---

## 🆘 Questions to Resolve Before Starting

If ANY of the following are unclear, ASK before implementing:
- MongoDB Atlas setup process unclear?
- Email service configuration uncertain?
- Design token usage not obvious from existing CSS?
- Session management approach needs clarification?
- Search history storage strategy needs discussion?
- Any security concerns or best practices to confirm?

**DO NOT GUESS** - Clarify uncertainties first!

---

**END OF PROMPT**
