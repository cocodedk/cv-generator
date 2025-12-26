# Common Issues

Common problems and their solutions when working with the CV Generator.

## Docker Issues

**Container Not Found**: Check with `docker-compose ps`, start with `docker-compose up -d`.

**Port Already in Use**: Find process (`lsof -i :8000` or `netstat -ano | findstr :8000`), stop it or change port.

**Database Connection Failed**: Check Neo4j is running, wait 30-60s for startup, check logs, verify `.env` variables.

## Backend Issues

**Import Errors**: Rebuild Docker image: `docker-compose build app && docker-compose up -d`.

**Pytest Import File Mismatch**: If you see "import file mismatch" errors, check for duplicate test files (both `.py` file and directory with same name). Remove the duplicate file and clear `__pycache__` directories: `find backend/tests -type d -name __pycache__ -exec rm -rf {} +`.

**Database Query Errors**: Check Neo4j accessible (http://localhost:7474), verify credentials, check query syntax, verify data format.

## Frontend Issues

**Dependencies Not Found**: Run `npm install` or `rm -rf node_modules package-lock.json && npm install`.

**API Connection Failed**: Verify backend running (http://localhost:8000/docs), check CORS config, verify API URL, check console.

**HMR Not Working**: Restart dev server, clear browser cache, check Vite config.

## Database Issues

**Neo4j Won't Start**: Check logs (`docker-compose logs neo4j`), recreate (`docker-compose down -v && docker-compose up -d neo4j`).

**Data Not Persisting**: Verify volume mounted (`docker volume ls`), check docker-compose.yml, don't use `-v` flag with down.

**Profile Save Memory Error**: Fixed in UPDATE_QUERY - profile updates now delete nodes separately to avoid cartesian products. If you encounter memory errors, see [Profile Memory Error Investigation](profile-memory-error-investigation.md).

## File Generation Issues

**DOCX Not Generated**: Check `backend/output/` exists, verify permissions, check logs, verify CV data.

**Download Fails**: Verify file exists, check filename validation, verify permissions, check console.

## Getting More Help

1. Check application logs: `docker-compose logs -f`
2. Check browser console for frontend errors
3. Review API documentation: http://localhost:8000/docs
4. See [Debugging Guide](debugging.md) for advanced troubleshooting

For more details, see [Development Setup](../development/setup.md) and [Docker Setup](../deployment/docker.md).
