# ⚡ Performance Monitoring Guide for Octa Music

## Overview
This guide provides comprehensive performance monitoring strategies, metrics, and optimization techniques for Octa Music.

---

## 🎯 Performance Targets

### Core Web Vitals (Target: Lighthouse Score >90)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Largest Contentful Paint (LCP)** | <2.5s | TBD | 🟡 Measure |
| **First Input Delay (FID)** | <100ms | TBD | 🟡 Measure |
| **Cumulative Layout Shift (CLS)** | <0.1 | TBD | 🟡 Measure |
| **Time to First Byte (TTFB)** | <600ms | TBD | 🟡 Measure |
| **Speed Index** | <3.0s | TBD | 🟡 Measure |

### Backend Performance Targets

| Metric | Target | Priority |
|--------|--------|----------|
| API Response Time (p95) | <200ms | High |
| API Response Time (p99) | <500ms | Medium |
| Database Query Time (p95) | <100ms | High |
| Home Page Load Time | <1.5s | High |
| Search Results Time | <2.0s | High |
| Error Rate | <0.1% | Critical |

---

## 📊 Key Performance Indicators (KPIs)

### 1. Application Performance

#### Response Time Metrics
```python
# Monitor these endpoints specifically:
- GET  /                      # Home page
- POST /api/v1/spotify/search # Spotify search
- POST /api/v1/youtube/search # YouTube search
- POST /api/auth/login        # Login
- GET  /api/v1/health         # Health check

# Target response times (p95):
# - Health check: <50ms
# - Home page: <200ms
# - Search endpoints: <500ms (depends on external API)
# - Auth endpoints: <300ms
```

#### Throughput Metrics
- **Requests per second (RPS)**: Current capacity
- **Concurrent users**: Max simultaneous users
- **Request distribution**: Which endpoints are most used

### 2. Resource Utilization

#### CPU Usage
- **Target**: <70% average, <90% peak
- **Alert**: >80% for more than 5 minutes

#### Memory Usage
- **Target**: <400MB (free tier: 512MB RAM)
- **Alert**: >450MB sustained

#### Disk I/O
- **Target**: <70% utilization
- **Alert**: High I/O wait times

### 3. External Dependencies

#### Spotify API
- **Average response time**: Monitor trends
- **Error rate**: <1%
- **Rate limit usage**: Track API quota

#### YouTube API
- **Average response time**: Monitor trends
- **Error rate**: <1%
- **Daily quota usage**: Track against limits

#### MongoDB Atlas
- **Connection pool**: Monitor active connections
- **Query time**: Track slow queries (>100ms)
- **Connection errors**: Should be 0

---

## 🔍 Monitoring Tools & Setup

### 1. Built-in Render Monitoring

**Access**: Render Dashboard → Your Service → Metrics

**Available Metrics**:
- CPU usage over time
- Memory usage over time
- Request rate (requests/second)
- Response time (average)
- Error rate (5xx errors)
- Build and deploy history

### 2. Application Logging

**Log Levels**:
```python
DEBUG   - Detailed debugging information (development only)
INFO    - General information about application flow
WARNING - Warning about potential issues
ERROR   - Error occurred but application continues
CRITICAL - Critical error, application may fail
```

**What to Log**:
```python
# Performance-related logs
logger.info(f"Spotify search completed in {duration:.2f}s")
logger.warning(f"Slow query detected: {query_time:.2f}s")
logger.error(f"External API timeout: {api_name}")

# Security-related logs
logger.warning(f"Rate limit exceeded: {ip_address}")
logger.warning(f"Failed login attempt: {username}")

# Business metrics
logger.info(f"User registered: {user_id}")
logger.info(f"Search performed: {search_query}")
```

### 3. Health Check Endpoint

**Endpoint**: `/api/v1/health`

**Current Response**:
```json
{
  "success": true,
  "error": null,
  "data": {
    "status": "healthy",
    "version": "1.0.0"
  }
}
```

**Enhanced Health Check** (Future):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-07T12:00:00Z",
  "dependencies": {
    "database": "healthy",
    "spotify_api": "healthy",
    "youtube_api": "healthy"
  },
  "metrics": {
    "uptime": 86400,
    "memory_usage": "256MB",
    "cpu_usage": "45%"
  }
}
```

---

## 📈 Performance Optimization Strategies

### 1. Database Optimization

#### Indexing Strategy
```javascript
// MongoDB indexes to create
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "username": 1 }, { unique: true })
db.search_history.createIndex({ "user_id": 1, "timestamp": -1 })
db.search_history.createIndex({ "timestamp": -1 })

// Verify indexes
db.users.getIndexes()
```

#### Query Optimization
```python
# Good: Use projection to fetch only needed fields
db.users.find(
    {"email": email},
    {"_id": 1, "username": 1, "email": 1, "password_hash": 1}
)

# Good: Use limit for pagination
db.search_history.find(
    {"user_id": user_id}
).sort("timestamp", -1).limit(20)

# Bad: Fetch entire document when not needed
db.users.find({"email": email})  # Returns all fields
```

#### Connection Pooling
```python
# MongoDB connection pool settings (already configured)
# maxPoolSize: 50 (default)
# minPoolSize: 10 (default)
# Monitor: Active connections should be < maxPoolSize
```

### 2. Response Caching

#### Browser Caching (Static Assets)
```python
# Add to main.py or create middleware
@app.after_request
def add_cache_headers(response):
    if request.path.startswith('/static/'):
        # Cache static assets for 1 year
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return response
```

#### API Response Caching (Future Enhancement)
```python
# Use Flask-Caching for frequently accessed data
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'simple',  # Use Redis in production
    'CACHE_DEFAULT_TIMEOUT': 300
})

@app.route('/api/v1/popular-artists')
@cache.cached(timeout=3600)  # Cache for 1 hour
def get_popular_artists():
    # Expensive operation
    pass
```

### 3. Response Compression

**Already Implemented**: Flask-Compress with Brotli

**Configuration**:
```python
# Automatic compression for:
# - Responses > 500 bytes
# - MIME types: text/html, text/css, application/json, etc.
# - Compression level: 6 (balanced)
```

**Verify Compression**:
```bash
# Check response headers
curl -I -H "Accept-Encoding: br, gzip" https://octa-music.onrender.com/

# Should see:
# Content-Encoding: br  (Brotli) or gzip
# Vary: Accept-Encoding
```

### 4. Image Optimization

**Current Implementation**:
- Lazy loading: `<img loading="lazy">`
- External CDN: Spotify and YouTube serve optimized images

**Future Enhancements**:
- Implement responsive images with `srcset`
- Use WebP format with fallback
- Implement image CDN (Cloudinary, imgix)

### 5. Code Optimization

#### Async Operations (Future)
```python
# For I/O-bound operations, consider async/await
import asyncio
import aiohttp

async def fetch_artist_data(artist_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

#### Database Query Batching
```python
# Good: Batch operations
user_ids = [user1_id, user2_id, user3_id]
users = db.users.find({"_id": {"$in": user_ids}})

# Bad: Multiple individual queries
for user_id in user_ids:
    user = db.users.find_one({"_id": user_id})
```

---

## 🚦 Performance Testing

### 1. Load Testing with Apache Bench

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Basic load test (100 requests, 10 concurrent)
ab -n 100 -c 10 https://octa-music.onrender.com/

# POST request test
ab -n 100 -c 10 -p data.json -T application/json \
   https://octa-music.onrender.com/api/v1/spotify/search

# data.json content:
# {"artist_name": "Test Artist"}
```

**Interpret Results**:
```
Time per request:     250.0 ms (mean)  # Should be <300ms
Requests per second:  40.0             # Current capacity
Failed requests:      0                # Should be 0
```

### 2. Load Testing with k6

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 10 },   // Stay at 10 users
    { duration: '30s', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],    // Error rate <1%
  },
};

export default function () {
  // Test home page
  let res = http.get('https://octa-music.onrender.com/');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
}
```

**Run k6 test**:
```bash
k6 run load-test.js
```

### 3. Browser Performance Testing

**Chrome DevTools**:
1. Open DevTools (F12)
2. Go to "Lighthouse" tab
3. Select "Performance" and "Best Practices"
4. Run audit
5. Target: >90 score on all metrics

**Key Metrics to Check**:
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Time to Interactive (TTI)
- Total Blocking Time (TBT)
- Cumulative Layout Shift (CLS)

---

## 📉 Performance Degradation Alerts

### Alert Thresholds

#### Critical Alerts (Immediate Action)
- Error rate >1% for 5 minutes
- Response time p95 >1000ms for 5 minutes
- Health check failing
- CPU >90% for 5 minutes
- Memory >90% for 5 minutes

#### Warning Alerts (Monitor Closely)
- Error rate >0.5% for 10 minutes
- Response time p95 >500ms for 10 minutes
- CPU >70% for 10 minutes
- Memory >70% for 10 minutes
- Slow queries >200ms

### Alert Actions

#### High Error Rate
1. Check recent deploys (rollback if needed)
2. Check external API status
3. Review error logs for patterns
4. Check database connectivity

#### Slow Response Times
1. Check database query performance
2. Check external API latency
3. Review recent code changes
4. Check resource utilization
5. Consider scaling up

#### High Resource Usage
1. Check for memory leaks
2. Review worker configuration
3. Optimize database queries
4. Consider scaling up
5. Review caching strategy

---

## 📊 Performance Dashboard (Recommended)

### Metrics to Display

#### Real-Time Metrics
- Current requests per second
- Current error rate
- Current response time (p50, p95, p99)
- Active users
- Resource utilization (CPU, Memory)

#### Historical Metrics (24 hours)
- Response time trends
- Error rate trends
- Request volume trends
- Resource utilization trends

#### Business Metrics
- User registrations per day
- Searches per day
- Active users per hour
- Popular search terms

---

## 🔧 Performance Troubleshooting

### Symptom: Slow Response Times

**Check**:
1. External API latency (Spotify, YouTube)
2. Database query times
3. Resource utilization (CPU, Memory)
4. Network connectivity

**Solutions**:
- Implement caching for API responses
- Optimize database queries with indexes
- Increase worker threads
- Upgrade Render plan

### Symptom: High Memory Usage

**Check**:
1. Memory leaks in application code
2. Large objects in memory
3. Session storage size
4. Cache size

**Solutions**:
- Review and fix memory leaks
- Implement pagination for large datasets
- Clean up old sessions
- Configure cache limits

### Symptom: High CPU Usage

**Check**:
1. Inefficient algorithms
2. Large data processing
3. Too many concurrent requests
4. Infinite loops or recursion

**Solutions**:
- Optimize algorithms
- Implement background processing
- Add rate limiting
- Review recent code changes

---

## 📅 Performance Review Schedule

### Daily
- [ ] Review response time trends
- [ ] Check error rates
- [ ] Monitor resource utilization

### Weekly
- [ ] Analyze slow queries
- [ ] Review external API performance
- [ ] Check cache hit rates
- [ ] Optimize underperforming endpoints

### Monthly
- [ ] Run full load tests
- [ ] Review and optimize database indexes
- [ ] Analyze performance trends
- [ ] Update performance targets
- [ ] Run Lighthouse audits

### Quarterly
- [ ] Comprehensive performance audit
- [ ] Review and upgrade dependencies
- [ ] Capacity planning
- [ ] Load testing with peak scenarios
- [ ] Performance optimization sprint

---

## 🎯 Performance Optimization Roadmap

### Phase 1: Quick Wins (Week 1-2)
- [x] Enable response compression
- [x] Implement security headers
- [x] Add database indexes
- [ ] Optimize image loading
- [ ] Add browser caching for static assets

### Phase 2: Caching (Week 3-4)
- [ ] Implement Redis caching
- [ ] Cache API responses
- [ ] Cache session data in Redis
- [ ] Implement CDN for static assets

### Phase 3: Advanced (Month 2-3)
- [ ] Implement async operations
- [ ] Add service worker for PWA
- [ ] Optimize bundle size
- [ ] Implement lazy loading for routes
- [ ] Add APM tool (DataDog/New Relic)

### Phase 4: Scaling (Month 4+)
- [ ] Implement horizontal scaling
- [ ] Add read replicas for database
- [ ] Implement microservices architecture
- [ ] Add message queue for background jobs
- [ ] Implement auto-scaling policies

---

## 📞 Support & Resources

### Performance Tools
- **Lighthouse**: https://developers.google.com/web/tools/lighthouse
- **WebPageTest**: https://www.webpagetest.org/
- **GTmetrix**: https://gtmetrix.com/
- **k6**: https://k6.io/

### Documentation
- **Flask Performance**: https://flask.palletsprojects.com/en/latest/deploying/
- **Gunicorn Tuning**: https://docs.gunicorn.org/en/stable/settings.html
- **MongoDB Performance**: https://docs.mongodb.com/manual/administration/analyzing-mongodb-performance/

---

**Last Updated**: 2024-01-07  
**Version**: 1.0  
**Next Review**: 2024-02-07
