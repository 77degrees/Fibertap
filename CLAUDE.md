# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fibertap is a personal/family data privacy monitoring tool that:
- Monitors for personal data exposure across the web (data brokers, breaches, people-search sites)
- Tracks family members' data exposure in a unified dashboard
- Integrates with Incogni to automate data removal requests
- Provides alerts when new exposures are detected

## Technology Stack

*To be determined* - This is a new project. When the stack is chosen, update this section with:
- Build commands
- Test commands
- Lint commands
- Development server commands

## Architecture

*To be established* - Key architectural decisions will be documented in `.claude/tech-lead.md`.

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
