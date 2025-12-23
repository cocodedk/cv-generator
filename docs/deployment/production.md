# Production Deployment

Guide for deploying the CV Generator to production.

## Prerequisites

- Docker and Docker Compose installed on server
- Domain name configured (optional)
- SSL certificate (for HTTPS)
- Reverse proxy (nginx recommended)

## Environment Configuration

### Environment Variables

Create `.env` file with production values:

```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<strong-password>
NEO4J_DATABASE=neo4j
CORS_ORIGINS=https://yourdomain.com
```

**Security Notes**:
- Use strong, unique passwords
- Never commit `.env` to version control
- Use Docker secrets for sensitive data

## Docker Compose for Production

Modify `docker-compose.yml` for production:

1. **Remove volume mounts** (use built images)
2. **Set resource limits**
3. **Configure health checks**
4. **Use production images**

## Reverse Proxy Setup

**Nginx Example**:
```nginx
server {
    listen 80; server_name yourdomain.com;
    location / { proxy_pass http://localhost:8000; proxy_set_header Host $host; }
}
```

## SSL/TLS Setup

Use Let's Encrypt: `certbot --nginx -d yourdomain.com`

## Database Backup

**Manual**: `docker-compose exec neo4j neo4j-admin backup --backup-dir=/backups`
**Automated** (cron): `0 2 * * * docker-compose exec neo4j neo4j-admin backup --backup-dir=/backups`

## Monitoring

### Health Checks

Monitor application health:
- API health endpoint: `/api/health`
- Docker health checks configured in Dockerfile

### Logging

Configure log aggregation:
- Use Docker logging drivers
- Set up log rotation
- Monitor error rates

## Scaling

For high traffic:
1. Use load balancer
2. Scale backend containers
3. Use Neo4j cluster
4. Implement caching layer

## Security Checklist

- [ ] Strong database passwords
- [ ] CORS configured for production domains
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Rate limiting implemented
- [ ] Input validation enabled
- [ ] Regular security updates

## Maintenance

**Update application**: `git pull && docker-compose build && docker-compose up -d`

**Database maintenance**: Regular backups, monitor disk space, review query performance.
