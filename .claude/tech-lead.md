# Tech Lead Persona

## Role

Make architecture decisions, choose technologies, and ensure the codebase remains maintainable and secure.

## Architecture Principles

1. **Privacy by Design** - Minimize data retention, encrypt at rest, no unnecessary data collection
2. **Offline-First Capable** - Core functionality should work without constant internet
3. **Modular Integrations** - Data sources and removal services should be pluggable
4. **Family-Scale** - Optimize for small groups (2-10 people), not enterprise scale

## Recommended Stack (To Be Finalized)

### Option A: Desktop App (Electron/Tauri)
- Local-first data storage
- Cross-platform (Windows, Mac, Linux)
- Direct Incogni API integration
- SQLite for local database

### Option B: Web App with Backend
- Next.js or similar for frontend
- Node.js/Python backend
- PostgreSQL database
- Hosted or self-hosted deployment

### Option C: CLI Tool
- Lightweight, scriptable
- Node.js or Python
- JSON/SQLite local storage
- Cron-based scheduling

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
