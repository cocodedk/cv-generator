# Contributing to CV Generator

## Local Setup
1. Install Docker Engine 20.10+ and Docker Compose 2.0+.
2. Install Node.js 20+ and npm 9+.
3. Clone the repository and install frontend dependencies: `npm install`.
4. Copy `.env.example` to `.env` and configure as needed.
5. Start backend and database: `docker-compose up -d`.

## Install Git Hooks
```
./scripts/install-hooks.sh
```

## Local Git Setup
Run these once after cloning:
```bash
git config pull.rebase true
git config core.autocrlf input
git config push.autoSetupRemote true
git config init.defaultBranch main
```
Windows contributors: use `core.autocrlf true` instead of `input`.

## Build and Test Commands
```bash
npm run dev:full                # Start full dev environment
npm run type-check              # TypeScript type checking
npm run lint:frontend           # Lint frontend (ESLint)
npm run lint:backend:local      # Lint backend (flake8, local)
npm run test:frontend           # Run frontend tests (Vitest)
npm run test:backend:local      # Run backend tests (pytest, local)
npm test                        # Run all tests
npm run build                   # Build frontend for production
```

## Coding Style
- TypeScript with strict mode — no `any`
- Python with flake8 + black formatting
- Files must not exceed 150 lines of code
- One class per file
- Follow DRY principle — avoid code duplication
- Follow Conventional Commits for all commit messages

## Branch Naming
| Branch prefix | Use for |
|---|---|
| `feature/` | New features (`feat:`) |
| `fix/` | Bug fixes (`fix:`) |
| `chore/` | Maintenance (`chore:`) |
| `docs/` | Documentation (`docs:`) |
| `refactor/` | Code refactoring (`refactor:`) |
| `ci/` | CI changes (`ci:`) |

Branch names use kebab-case. Never commit directly to `main` — always open a PR.

## PR Checklist
- [ ] All tests pass (`npm test`)
- [ ] TypeScript type check passes (`npm run type-check`)
- [ ] Linting passes (frontend + backend)
- [ ] Manual test completed for changed functionality
- [ ] Updated docs if behavior changed
- [ ] Commit messages follow Conventional Commits format
