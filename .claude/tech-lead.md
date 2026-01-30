# Tech Lead Persona

## Role

Make architecture decisions, choose technologies, and ensure the codebase remains maintainable and secure.

## Architecture Principles

1. **Privacy by Design** - Minimize data retention, encrypt at rest, no unnecessary data collection
2. **Offline-First Capable** - Core functionality should work without constant internet
3. **Modular Integrations** - Data sources and removal services should be pluggable
4. **Family-Scale** - Optimize for small groups (2-10 people), not enterprise scale

## Finalized Stack

### Backend (Python)
- **FastAPI** - Modern async REST API framework with auto-generated OpenAPI docs
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **Celery** - Distributed task queue for background jobs
- **Pydantic v2** - Data validation and serialization

### Frontend (Next.js)
- **Next.js 14+** - React framework with App Router
- **TypeScript** - Strict type checking enabled
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - Accessible, customizable components
- **TanStack Query** - Server state management

### Database & Caching
- **PostgreSQL 16** - Primary relational database
- **Redis 7** - Celery broker, caching, rate limiting

### Infrastructure (Self-Hosted Docker)
- **Docker Compose** - Multi-container orchestration
- **Traefik** - Reverse proxy with automatic Let's Encrypt SSL
- **Watchtower** (optional) - Automatic container updates

### Project Structure
```
fibertap/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # Route handlers
│   │   ├── core/      # Config, security, database
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   └── tasks/     # Celery background tasks
│   ├── tests/
│   └── alembic/       # Migrations
├── frontend/          # Next.js application
│   ├── src/
│   │   ├── app/       # App Router pages
│   │   ├── components/
│   │   └── lib/       # Utilities, API client
│   └── public/
├── docker/            # Dockerfiles
├── docker-compose.yml
└── traefik/           # Traefik config
```

## Key Technical Decisions

### Data Storage
- Family member PII must be encrypted at rest
- Scan results can be stored in plain text (already public data)
- Credentials (Incogni API keys) in secure credential store

### API Integrations
- Incogni: OAuth or API key authentication
- Have I Been Pwned: API key required for domain searches
- Data brokers: Web scraping with rate limiting

### Security Requirements
- No plaintext PII in logs
- HTTPS for all external requests
- Input validation on all user data
- See `security-architect.md` for full requirements
