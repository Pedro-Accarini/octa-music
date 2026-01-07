# 🚀 Deployment Best Practices for Octa Music

## Production Deployment Checklist

### Pre-Deployment (P0 - Must Complete)
- [ ] All environment variables configured in Render dashboard
- [ ] SECRET_KEY is cryptographically secure (64+ characters)
- [ ] Database backups configured
- [ ] Health check endpoint tested: `/api/v1/health`
- [ ] SSL/TLS certificate active and valid
- [ ] All API keys rotated and stored securely
- [ ] SESSION_COOKIE_SECURE=true in production
- [ ] APP_ENV=production set correctly

### Environment Variables Configuration

#### Required Secrets (Set in Render Dashboard)
```bash
# Application
SECRET_KEY=<generate-with-secrets-token>  # Use: python -c "import secrets; print(secrets.token_hex(32))"
APP_ENV=production
FLASK_ENV=production

# Spotify API
SPOTIPY_CLIENT_ID=<your-spotify-client-id>
SPOTIPY_CLIENT_SECRET=<your-spotify-client-secret>

# YouTube API
YOUTUBE_API_KEY=<your-youtube-api-key>

# MongoDB
MONGODB_URI=<mongodb-connection-string>

# Email (Gmail SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=<your-email@gmail.com>
MAIL_PASSWORD=<app-specific-password>
MAIL_DEFAULT_SENDER=<your-email@gmail.com>

# Application URL
FRONTEND_URL=https://octa-music.onrender.com

# Session & Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=4800
REMEMBER_ME_DURATION=2592000

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
LOGIN_RATE_LIMIT_PER_MINUTE=3
LOGIN_RATE_LIMIT_PER_HOUR=10
```

---

## 🔧 Render.com Configuration

### Service Settings

#### Build Settings
```yaml
Build Command: pip install --upgrade pip && pip install -r requirements.txt
```

#### Start Settings
```yaml
Start Command: gunicorn --chdir src --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 --worker-class gthread --worker-tmp-dir /dev/shm --access-logfile - --error-logfile - --log-level info --preload main:app
```

**Gunicorn Configuration Explained:**
- `--workers 2`: Two worker processes for handling requests
- `--threads 4`: Four threads per worker (total 8 concurrent requests)
- `--worker-class gthread`: Use threaded workers for better concurrency
- `--worker-tmp-dir /dev/shm`: Use shared memory for better performance
- `--timeout 120`: 120 second timeout for long-running requests
- `--preload`: Load application before forking workers (faster startup)
- `--access-logfile -`: Log access to stdout
- `--error-logfile -`: Log errors to stdout

#### Health Check
```yaml
Health Check Path: /api/v1/health
```

#### Auto-Deploy
```yaml
Auto Deploy: Yes
Branch: main (production) or development (staging)
```

---

## 📊 Performance Optimization

### 1. Gunicorn Workers Configuration

For Render's free tier (512MB RAM):
- **Workers**: 2
- **Threads per worker**: 4
- **Total concurrent requests**: 8

Formula for optimal workers:
```
workers = (2 * CPU_CORES) + 1
threads = 4 (good balance for I/O-bound applications)
```

### 2. Response Compression
- Brotli compression enabled via Flask-Compress
- Automatic compression for responses >500 bytes
- MIME types: text/html, text/css, text/javascript, application/json

### 3. Static Asset Optimization
- Images: Use lazy loading (`loading="lazy"`)
- CSS/JS: Minify in production (future enhancement)
- Cache headers: Set appropriate cache-control headers

### 4. Database Query Optimization
- Use indexes on frequently queried fields
- Limit result sets with pagination
- Use projection to select only needed fields

```python
# Good: Only fetch needed fields
db.users.find({"email": email}, {"_id": 1, "username": 1, "email": 1})

# Bad: Fetch entire document
db.users.find({"email": email})
```

---

## 🔄 Zero-Downtime Deployment

### Strategy
1. **Health Check**: Render monitors `/api/v1/health`
2. **Rolling Update**: New instances start before old ones stop
3. **Automatic Rollback**: Failed health checks trigger rollback

### Pre-Deploy Tests
```bash
# Run tests locally
pytest tests/ -v

# Test build
pip install -r requirements.txt

# Test application startup
python src/main.py
```

### Post-Deploy Verification
1. Check health endpoint: `curl https://octa-music.onrender.com/api/v1/health`
2. Verify authentication flows (login, register, logout)
3. Test search functionality
4. Check error logs in Render dashboard
5. Monitor response times

---

## 📈 Monitoring & Alerting

### Key Metrics to Monitor

#### 1. Application Metrics
- **Response Time**: p50, p95, p99 latencies
- **Error Rate**: 5xx errors should be <0.1%
- **Request Rate**: Requests per second
- **CPU Usage**: Should stay <80%
- **Memory Usage**: Should stay <400MB (free tier)

#### 2. Database Metrics
- Connection pool usage
- Query execution time
- Failed queries
- Index hit rate

#### 3. Security Metrics
- Failed login attempts
- Rate limit hits
- Suspicious URL patterns
- Session anomalies

### Log Monitoring
```bash
# View logs in Render dashboard
# Filter by log level: INFO, WARNING, ERROR, CRITICAL

# Example log patterns to watch:
# - "Rate limit exceeded"
# - "Authentication failed"
# - "Database connection error"
# - "Suspicious URL pattern detected"
```

---

## 🔐 Secret Rotation Procedure

### 1. SECRET_KEY Rotation (Careful!)
⚠️ **Warning**: Rotating SECRET_KEY invalidates all active sessions

```bash
# Generate new secret
python -c "import secrets; print(secrets.token_hex(32))"

# Steps:
1. Schedule maintenance window
2. Update SECRET_KEY in Render dashboard
3. Trigger manual deploy
4. All users must re-login
5. Monitor for issues
```

### 2. API Key Rotation (Spotify, YouTube)
```bash
# Steps:
1. Generate new API key in respective platform
2. Update environment variable in Render
3. Trigger redeploy (automatic with new env var)
4. Verify API calls are working
5. Revoke old API key after 24 hours
```

### 3. Database Credentials Rotation
```bash
# Steps:
1. Create new database user with same permissions
2. Update MONGODB_URI in Render
3. Trigger redeploy
4. Verify application connectivity
5. Remove old database user after 24 hours
```

---

## 🚨 Incident Response Playbook

### P0 - Critical Issues (Immediate Response Required)

#### Application Down
1. **Check Render status**: https://status.render.com
2. **Check health endpoint**: `/api/v1/health`
3. **Review recent deploys**: Render dashboard → Events
4. **Check logs**: Look for errors in last 15 minutes
5. **Rollback if needed**: Render dashboard → Rollback to previous deploy

#### Database Connection Issues
1. **Check MongoDB Atlas status**
2. **Verify connection string**: MONGODB_URI
3. **Check IP whitelist**: Ensure Render IPs are whitelisted
4. **Test connection**: Use MongoDB Compass or CLI

#### High Error Rate
1. **Identify error pattern**: Check logs for common errors
2. **Check external API status**: Spotify, YouTube APIs
3. **Review recent code changes**: GitHub commits
4. **Implement hotfix if needed**

### P1 - High Priority (Response within 1 hour)

#### Slow Response Times
1. **Check resource usage**: CPU, Memory in Render dashboard
2. **Identify slow queries**: Database query logs
3. **Check external API latency**: Spotify, YouTube
4. **Consider scaling**: Upgrade Render plan if needed

#### Authentication Issues
1. **Check session configuration**: SESSION_COOKIE_SECURE, etc.
2. **Verify email service**: SMTP settings
3. **Check rate limiting**: May be blocking legitimate users
4. **Review recent auth code changes**

---

## 🧪 Testing in Production

### Smoke Tests (Run after each deploy)
```bash
# 1. Health check
curl https://octa-music.onrender.com/api/v1/health

# 2. Home page loads
curl -I https://octa-music.onrender.com/

# 3. API endpoint (Spotify search)
curl -X POST https://octa-music.onrender.com/api/v1/spotify/search \
  -H "Content-Type: application/json" \
  -d '{"artist_name": "Test Artist"}'

# 4. Authentication endpoints
curl -I https://octa-music.onrender.com/login
```

### Load Testing (Quarterly)
```bash
# Use Apache Bench or similar tool
ab -n 1000 -c 10 https://octa-music.onrender.com/

# Or use k6
k6 run load-test.js
```

---

## 📦 Backup & Recovery

### Database Backups
- **Frequency**: Daily automatic backups (MongoDB Atlas)
- **Retention**: 7 days (free tier) or 30 days (paid tier)
- **Manual Backup**: Before major deployments

### Recovery Procedure
```bash
# MongoDB Atlas
1. Go to MongoDB Atlas dashboard
2. Select Cluster → Backup
3. Choose restore point
4. Restore to new cluster or existing
5. Update MONGODB_URI if needed
```

### Configuration Backup
- All environment variables documented in this guide
- render.yaml in version control
- Infrastructure as code approach

---

## 🔄 Rollback Procedure

### Automatic Rollback (Render)
- Failed health checks trigger automatic rollback
- No manual intervention required

### Manual Rollback
```bash
# In Render Dashboard:
1. Go to Service → Deploys
2. Find last successful deploy
3. Click "Rollback to this deploy"
4. Confirm rollback
5. Monitor health and logs
```

### Database Migration Rollback
```bash
# If schema changes were made:
1. Identify migration to rollback
2. Run rollback script (if available)
3. Verify data integrity
4. Update application code if needed
```

---

## 📞 Support & Escalation

### Render Support
- **Dashboard**: https://dashboard.render.com
- **Docs**: https://render.com/docs
- **Status**: https://status.render.com
- **Support**: support@render.com (paid plans)

### External Services
- **MongoDB Atlas**: support.mongodb.com
- **Spotify API**: developer.spotify.com/support
- **YouTube API**: Google Cloud Console support

---

## 📅 Maintenance Schedule

### Daily
- [ ] Review application logs
- [ ] Check error rates
- [ ] Monitor performance metrics

### Weekly
- [ ] Review and clear old logs
- [ ] Check database performance
- [ ] Review security alerts

### Monthly
- [ ] Update dependencies (patch versions)
- [ ] Review and optimize slow queries
- [ ] Check SSL certificate expiry
- [ ] Review rate limiting effectiveness

### Quarterly
- [ ] Major dependency updates
- [ ] Security audit
- [ ] Load testing
- [ ] Disaster recovery drill
- [ ] Review and update documentation

---

## 🎯 Success Criteria

Application is production-ready when:
- [x] Zero critical security vulnerabilities
- [x] Health check endpoint responding <200ms
- [x] Error rate <0.1%
- [x] Uptime >99.9% over 30 days
- [x] All secrets properly managed
- [x] Monitoring and alerting configured
- [x] Backup and recovery tested
- [x] Documentation complete

---

**Last Updated**: 2024-01-07  
**Version**: 1.0  
**Maintained By**: DevOps Team
