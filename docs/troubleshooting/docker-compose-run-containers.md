# Docker Compose Run Containers Investigation

## Issue Description

When shutting down services with `docker-compose down`, the output shows containers with names like `cv_app_run_9352a22a27c6` being stopped and removed:

```
Shutting down services...
Stopping cv_app_run_9352a22a27c6 ... done
Stopping cv-app                  ... done
Stopping cv-neo4j                ... done
Removing cv-app                  ... done
Removing cv-neo4j                ... done
Removing network cv_cv-network
```

## Root Cause

The container name pattern `cv_app_run_<hash>` indicates that a container was created using `docker-compose run` command. This happens when:

1. **Manual execution without `--rm` flag**: Someone ran `docker-compose run app <command>` without the `--rm` flag, leaving the container running after the command completes.

2. **Interrupted command**: A command using `docker-compose run --rm` was interrupted (e.g., Ctrl+C) before the cleanup could occur, leaving the container behind.

3. **Fallback execution**: The scripts use `docker-compose run --rm` as a fallback when `docker-compose exec` fails (container not running), but if the fallback is interrupted, the container may persist.

## Where This Occurs

Looking at the codebase, `docker-compose run` is used in:

1. **package.json** (lines 15, 19, 22):
   - `test:backend`: `docker-compose exec -T app pytest || docker-compose run --rm app pytest`
   - `lint:backend`: `docker-compose exec -T app flake8 backend || docker-compose run --rm app flake8 backend`
   - `format:backend`: `docker-compose exec -T app black backend || docker-compose run --rm app black backend`

2. **scripts/run-tests.sh** (line 105):
   - `docker-compose exec -T app $PYTEST_CMD || docker-compose run --rm app $PYTEST_CMD`

All of these use the `--rm` flag, which should automatically remove containers when they exit. However, containers can persist if:
- The command is interrupted before cleanup
- Docker daemon issues prevent cleanup
- The container is manually created without `--rm`

## Is This a Problem?

**No, this is not a critical issue.** The behavior is expected:

1. **Normal Docker Compose behavior**: `docker-compose down` stops and removes ALL containers associated with the project, including those created by `docker-compose run`.

2. **No data loss**: These are temporary containers used for running one-off commands. They don't contain persistent data.

3. **Clean shutdown**: The containers are being properly stopped and removed during shutdown.

## How to Fix

### Option 1: Clean up orphaned containers manually (if needed)

If you want to clean up any orphaned `docker-compose run` containers before shutdown:

```bash
# List containers created by docker-compose run
docker ps -a --filter "name=cv_app_run" --format "{{.Names}}"

# Remove them manually
docker ps -a --filter "name=cv_app_run" --format "{{.Names}}" | xargs -r docker rm -f
```

### Option 2: Ensure `--rm` flag is always used

All scripts already use `--rm`, but if you manually run commands, always include it:

```bash
# Good - container auto-removes
docker-compose run --rm app pytest

# Bad - container persists
docker-compose run app pytest
```

### Option 3: Add cleanup to stop script (optional enhancement)

The `stop-dev.sh` script could be enhanced to clean up orphaned containers before running `docker-compose down`:

```bash
# Clean up any orphaned docker-compose run containers
docker ps -a --filter "name=cv_app_run" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true

# Then proceed with normal shutdown
docker-compose down
```

## Prevention

To prevent this from happening:

1. **Always use `--rm` flag**: When manually running `docker-compose run`, always include `--rm`
2. **Let commands complete**: Avoid interrupting `docker-compose run` commands if possible
3. **Use `docker-compose exec` when container is running**: Prefer `exec` over `run` when the container is already running

## Verification

To check if there are any orphaned containers:

```bash
# Check for containers created by docker-compose run
docker ps -a --filter "name=cv_app_run"

# Check all containers in the project
docker-compose ps -a
```

## Conclusion

The appearance of `cv_app_run_<hash>` containers during shutdown is **normal and expected behavior**. Docker Compose is correctly cleaning up all containers associated with the project, including temporary ones created by `docker-compose run`. This is not an error and doesn't indicate any problems with the application or Docker setup.

If you want to avoid seeing these containers during shutdown, ensure all `docker-compose run` commands use the `--rm` flag and complete successfully.
