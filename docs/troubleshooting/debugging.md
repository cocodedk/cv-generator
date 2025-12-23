# Debugging Guide

Advanced debugging techniques and tools for the CV Generator.

## Backend Debugging

### Viewing Logs

**Real-time logs**:
```bash
docker-compose logs -f app
```

**Filter logs**:
```bash
docker-compose logs app | grep ERROR
```

### Interactive Debugging

**Access container shell**:
```bash
docker-compose exec app bash
```

**Run Python interactively**:
```bash
docker-compose exec app python
```

**Test database connection**:
```bash
docker-compose exec app python -c "from backend.database.connection import Neo4jConnection; print(Neo4jConnection.verify_connectivity())"
```

### API Testing

**Using curl**:
```bash
# Health check
curl http://localhost:8000/api/health

# Create CV
curl -X POST http://localhost:8000/api/generate-cv \
  -H "Content-Type: application/json" \
  -d '{"personal_info": {"name": "Test"}}'
```

**Using Swagger UI**:
- Access http://localhost:8000/docs
- Test endpoints interactively
- View request/response schemas

## Frontend Debugging

### Browser DevTools

**Console**: View errors, log API responses, inspect network requests.
**Network Tab**: Monitor API calls, check request/response data, identify failures.
**React DevTools**: Install extension, inspect component state, debug props/hooks.

### Debugging Tips

**Console logs**: `console.log('Form data:', data)`, `console.error('API error:', error)`
**Breakpoints**: Use browser debugger, set breakpoints, step through execution.

## Database Debugging

**Neo4j Browser** (http://localhost:7474):
Queries: `MATCH (cv:CV) RETURN cv LIMIT 10`, `MATCH (cv:CV {id: 'id'}) RETURN cv`, `MATCH (n) RETURN labels(n), count(n)`

**Cypher Shell**: `docker-compose exec neo4j cypher-shell -u neo4j -p cvpassword`

## Performance Debugging

**Backend**: Add timing logs, use FastAPI middleware, monitor query performance.
**Database**: Use EXPLAIN in Cypher, monitor slow queries, check indexes.
**Frontend**: Use React DevTools Profiler, check network performance, optimize renders.

## Common Scenarios

**API 500 Error**: Check logs, verify DB connection, check validation, review stack trace.
**Form Submission Fails**: Check console, verify endpoint URL, check payload, review validation.
**Data Not Saving**: Check DB connection, verify query execution, check transactions, review logs.

See [Common Issues](common-issues.md) for more scenarios.
