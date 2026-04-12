# CLAUDE.md — CV Generator

## Project Overview

CV Generator is a full-stack application for generating professional CV documents with AI-powered assistance. It features a React + TypeScript frontend, Python FastAPI backend, and Neo4j graph database for CV storage and management.

- **Language / Runtime**: TypeScript (Node.js 20), Python 3.11
- **Framework**: React 18 + Vite (frontend), FastAPI + Uvicorn (backend)
- **Architecture**: REST API, React SPA, Neo4j graph database
- **Package / Namespace**: `cv-generator` / `backend`

---

## Required Skills — ALWAYS Invoke These

These skills **must** be invoked when the relevant situation arises. Never skip them.

| Situation | Skill |
|-----------|-------|
| Before any new feature or screen | `superpowers:brainstorming` |
| Planning multi-step changes | `superpowers:writing-plans` |
| Writing or fixing core logic | `superpowers:test-driven-development` |
| First sign of a bug or failure | `superpowers:systematic-debugging` |
| Before completing a feature branch | `superpowers:requesting-code-review` |
| Before claiming any task done | `superpowers:verification-before-completion` |
| Working on UI / frontend | `frontend-design:frontend-design` |
| After implementing — reviewing quality | `simplify` |

---

## Architecture

```
cv/
├── backend/                    ← Python FastAPI backend
│   ├── app.py                 ← Main FastAPI application
│   ├── app_helpers/           ← Routes, middleware, lifecycle
│   ├── cv_generator/          ← DOCX + HTML generation
│   ├── database/              ← Neo4j connection + queries
│   ├── models/                ← Pydantic models
│   ├── services/              ← AI service, file service
│   └── tests/                 ← pytest test suite
├── frontend/                  ← React TypeScript SPA
│   └── src/
│       ├── components/        ← React components
│       ├── app_helpers/       ← Form logic, rich text
│       ├── services/          ← API service layer
│       └── types/             ← TypeScript types
├── .github/workflows/         ← CI, release, pages automation
├── .githooks/                 ← pre-commit, commit-msg hooks
├── scripts/                   ← install-hooks.sh, setup-repo.sh
└── version.txt                ← semantic version (MAJOR.MINOR.PATCH)
```

### Layer Rules
- Frontend never imports from backend directly — REST API only
- Services in `backend/services/` contain all business logic
- Database queries are isolated in `backend/database/queries/`
- Files must not exceed 150 lines — one class per file

---

## Coding Conventions

- [ ] TypeScript strict mode — no `any` types
- [ ] Python with flake8 + black formatting
- [ ] All models are **immutable** where possible
- [ ] Functions are **pure** where possible
- [ ] No hardcoded strings — use constants or config

---

## Engineering Principles

### File Size
- **150-line maximum per file** — extract a class, function, or module when approaching the limit

### DRY · SOLID · KISS · YAGNI
- Extract shared logic into named utilities; never copy-paste
- Single Responsibility: one class/function does one thing
- Don't add features not yet needed
- Delete dead code immediately

### TDD
- Write the failing test first, make it pass, then refactor
- Backend: pytest with 70% coverage minimum
- Frontend: Vitest + React Testing Library
- Test names describe behaviour: `"should reject duplicate email"`

### Commit hygiene
- Follow Conventional Commits: `feat: ...` / `fix: ...` / `chore: ...`
- The `commit-msg` hook enforces this automatically

---

## Build Commands

```bash
npm run dev:full                # Start full dev environment (Docker + frontend)
npm run type-check              # TypeScript type check
npm run lint:frontend           # ESLint (frontend)
npm run lint:backend:local      # flake8 (backend, local)
npm run test:frontend           # Vitest (frontend)
npm run test:backend:local      # pytest (backend, local)
npm test                        # All tests
npm run build                   # Build frontend for production
```

---

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | This file — project conventions and session startup |
| `version.txt` | Semantic version (MAJOR.MINOR.PATCH) |
| `docker-compose.yml` | Backend + Neo4j containers |
| `.github/workflows/ci.yml` | CI on PRs and branches |
| `.github/workflows/release.yml` | GitHub Release automation |
| `.github/workflows/pages.yml` | GitHub Pages deployment |
| `.githooks/pre-commit` | Runs lint + tests before commit |
| `.githooks/commit-msg` | Enforces Conventional Commits |
| `scripts/install-hooks.sh` | One-time hook installer |
| `scripts/setup-repo.sh` | Branch protection + repo settings |

---

## Starting a New Session

1. Read this file
2. Run `npm run type-check && npm run test:frontend` to confirm everything passes
3. Invoke `superpowers:brainstorming` before touching any feature
4. Follow the Required Skills table — every skill is mandatory, not optional
