# Deployment Guide - Phase 8

## Production Checklist

### Before Deployment
- [ ] All tests passing (Phase 7)
- [ ] Environment variables configured
- [ ] Database migrations complete
- [ ] API documentation up-to-date
- [ ] Security review complete
- [ ] Performance benchmarks acceptable
- [ ] Error handling verified
- [ ] Logging configured
- [ ] Backup strategy in place

### Security Hardening
- [ ] Add authentication (JWT/OAuth2)
- [ ] Implement rate limiting
- [ ] Add input validation
- [ ] Set CORS properly
- [ ] Use HTTPS/TLS
- [ ] Sanitize user inputs
- [ ] Hash sensitive data
- [ ] Implement request signing

### Performance Optimization
- [ ] Add caching layer (Redis)
- [ ] Optimize database queries
- [ ] Compress API responses
- [ ] Add CDN for static assets
- [ ] Enable gzip compression
- [ ] Lazy load documents
- [ ] Implement pagination
- [ ] Add monitoring/alerts

---

## Deployment Platforms

### 1. Docker Compose (Local/VPS)
```bash
docker-compose up -d
# See DOCKER.md for details
```

### 2. AWS
- **Option A**: ECS Fargate (serverless containers)
- **Option B**: EC2 (traditional VM)
- **Option C**: Lambda (serverless functions)
- **Option D**: Elastic Beanstalk (managed platform)

### 3. Google Cloud
- Cloud Run (serverless containers)
- Compute Engine (VMs)
- App Engine (managed platform)

### 4. Azure
- Container Instances
- App Service
- Virtual Machines
- Kubernetes Service (AKS)

### 5. Heroku
```bash
git push heroku main
```

### 6. DigitalOcean
- App Platform (managed)
- Droplets (VMs)
- Kubernetes (DOKS)

### 7. Self-Hosted
- Docker + reverse proxy (nginx)
- Kubernetes cluster
- Virtual private server

---

## Step-by-Step Deployment (AWS ECS Example)

### 1. Prepare Code
```bash
cd rag-system
git init
git add .
git commit -m "Phase 7-8: Complete RAG system"
```

### 2. Create ECR Repository
```bash
aws ecr create-repository --repository-name rag-backend
aws ecr create-repository --repository-name rag-frontend
```

### 3. Build & Push Images
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login \
  --username AWS \
  --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
docker build -f Dockerfile.backend -t rag-backend .
docker tag rag-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest

# Build and push frontend
docker build -f Dockerfile.frontend -t rag-frontend .
docker tag rag-frontend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/rag-frontend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/rag-frontend:latest
```

### 4. Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name rag-system
```

### 5. Create Task Definitions
```bash
# See task-definition.json for ECS task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

### 6. Create Service
```bash
aws ecs create-service \
  --cluster rag-system \
  --service-name rag-backend \
  --task-definition rag-backend:1 \
  --desired-count 2 \
  --load-balancers targetGroupArn=arn:aws:...,containerName=rag-backend,containerPort=8000
```

### 7. Configure Load Balancer
- Create Application Load Balancer
- Configure target groups
- Set up health checks
- Configure SSL/TLS

### 8. Set Up Auto-Scaling
```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name rag-backend-asg \
  --desired-capacity 2 \
  --min-size 2 \
  --max-size 10
```

---

## Monitoring & Logging

### CloudWatch (AWS)
```bash
# View logs
aws logs tail /ecs/rag-backend --follow

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name rag-api-errors \
  --alarm-description "Alert on API errors" \
  --metric-name Errors \
  --threshold 10
```

### Datadog Integration
```python
# Add to app.py
from datadog import initialize, api
import logging

logger = logging.getLogger(__name__)
handler = logging.handlers.DatadogLogHandler(hostname="localhost", port=10518)
logger.addHandler(handler)
```

### New Relic
```python
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
app = newrelic.agent.WSGIApplicationWrapper(app)
```

---

## Scaling Strategies

### Horizontal Scaling (Add More Servers)
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rag-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rag-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Vertical Scaling (Bigger Server)
- Increase CPU/RAM allocation
- Use faster storage (SSD)
- Upgrade database tier

### Database Optimization
- Add read replicas
- Implement caching (Redis)
- Partition large tables
- Archive old documents

---

## Disaster Recovery

### Backup Strategy
```bash
# Daily backups
0 2 * * * /scripts/backup-db.sh

# Store in S3
aws s3 sync ./backups s3://rag-backups/
```

### Recovery Procedure
1. Restore from backup
2. Verify data integrity
3. Update DNS (if needed)
4. Test all functionality
5. Monitor for issues

### High Availability
```yaml
# Multi-region deployment
- Region: us-east-1 (primary)
- Region: eu-west-1 (replica)
- Database replication: Active-Active
- Failover: Automatic via Route 53
```

---

## Cost Optimization

### Reduce Compute Costs
- Use spot instances (70% cheaper)
- Right-size instances
- Scale down during off-hours
- Use serverless where possible

### Reduce Storage Costs
- Archive old documents
- Compress backups
- Use S3 Glacier
- Clean up logs regularly

### Reduce Data Transfer Costs
- Use CDN (CloudFront)
- Compress responses
- Limit batch sizes
- Cache responses

---

## Rollback Plan

### Canary Deployment
```bash
# Deploy to 10% of traffic
aws ecs update-service \
  --cluster rag-system \
  --service rag-backend \
  --force-new-deployment

# Monitor metrics for 10 minutes
# If OK: increase to 50%, then 100%
# If bad: rollback to previous version
```

### Blue-Green Deployment
```bash
# Deploy to "green" environment
# Run tests
# Swap traffic from "blue" to "green"
# Keep "blue" ready for rollback
```

### Database Migrations
```bash
# Safe migration procedure
1. Create backup
2. Test on staging
3. Run migration during maintenance window
4. Verify data integrity
5. Monitor performance
6. Keep rollback script ready
```

---

## Post-Deployment

### Verify Deployment
```bash
# Health checks
curl https://api.example.com/health
curl https://example.com/

# Monitor logs
tail -f /var/log/rag-backend.log

# Check metrics
- CPU usage: 30-50%
- Memory: 40-60%
- Error rate: < 0.1%
- Response time: < 500ms
```

### Security Verification
```bash
# SSL certificate
openssl s_client -connect api.example.com:443

# Security headers
curl -I https://api.example.com

# CORS configuration
curl -H "Origin: http://example.com" https://api.example.com
```

### Performance Testing
```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 http://api.example.com/api/health

# Load testing with wrk
wrk -t12 -c400 -d30s http://api.example.com/api/health
```

---

## Documentation Updates

- [ ] Update README with production URLs
- [ ] Document API endpoints with auth
- [ ] Create operations runbook
- [ ] Document monitoring dashboards
- [ ] Create incident response procedures
- [ ] Document data retention policies
- [ ] Create user guides
- [ ] Document admin procedures

---

## Compliance & Compliance

### Data Protection
- [ ] GDPR compliance (if EU users)
- [ ] CCPA compliance (if CA users)
- [ ] HIPAA compliance (if healthcare)
- [ ] PCI DSS compliance (if payment processing)

### Auditing
- [ ] Log all API calls
- [ ] Track data access
- [ ] Monitor permission changes
- [ ] Regular security audits

### Backups
- [ ] Automated daily backups
- [ ] Test restore procedures
- [ ] Store in multiple regions
- [ ] Encrypt backup data

---

## Success Metrics

- Response time: < 500ms (p95)
- Availability: > 99.5%
- Error rate: < 0.1%
- CPU usage: 30-70%
- Memory usage: 40-70%
- Successful deploys: 100%
- MTTR: < 30 minutes

---

## Support & Maintenance

### Update Cycle
- Security patches: Immediately
- Bug fixes: Weekly
- Feature updates: Monthly
- Major upgrades: Quarterly

### Maintenance Windows
- Schedule: Sundays 2-4 AM UTC
- Duration: 30-60 minutes
- Notification: 7 days notice

### On-Call Rotation
- 24/7 support for critical issues
- 4-hour response time for non-critical
- Escalation procedure defined

---

**Status: Phase 8 Complete - Ready for Production Deployment**
