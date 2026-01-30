# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fibertap is a personal/family data privacy monitoring tool that:
- Monitors for personal data exposure across the web (data brokers, breaches, people-search sites)
- Tracks family members' data exposure in a unified dashboard
- Integrates with Incogni to automate data removal requests
- Provides alerts when new exposures are detected

## Technology Stack

### Backend (Python)
- **FastAPI** - Async REST API framework
- **SQLAlchemy** - ORM
- **Celery + Redis** - Background job processing
- **Pydantic** - Data validation

### Frontend (Next.js)
- **Next.js 14+** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library

### Database
- **PostgreSQL** - Primary data store
- **Redis** - Job queue and caching

### Infrastructure
- **Docker Compose** - Container orchestration
- **Traefik** - Reverse proxy with auto SSL

## Development Commands

```bash
# Start all services
docker compose up -d

# Backend (from /backend)
cd backend
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (from /frontend)
cd frontend
npm install
npm run dev

# Run tests
cd backend && pytest
cd frontend && npm test

# Linting
cd backend && ruff check . && mypy .
cd frontend && npm run lint
```

## Architecture

Self-hosted web application with separate frontend and backend services:

- **Frontend**: Next.js serves the dashboard UI, communicates with backend via REST API
- **Backend**: FastAPI handles API requests, business logic, and coordinates with external services
- **Workers**: Celery processes background jobs (scanning, monitoring, Incogni sync)
- **Database**: PostgreSQL stores family members, scan results, removal request status
- **Cache/Queue**: Redis for Celery task queue and API response caching

See `.claude/tech-lead.md` for detailed architecture decisions.

## Key Integrations

- **Incogni API**: Primary integration for submitting and tracking data removal requests
- **Data Breach Databases**: Sources for monitoring exposure (Have I Been Pwned, etc.)
- **Data Broker Detection**: Scanning people-search and data broker sites

## Project Personas

See `.claude/` directory for role-specific guidance:
- `project.md` - Overall project description
- `product-manager.md` - Product vision and scope
- `tech-lead.md` - Architecture decisions
- `developer.md` - Coding standards
- `qa-engineer.md` - Testing guidelines
- `security-architect.md` - Security requirements
