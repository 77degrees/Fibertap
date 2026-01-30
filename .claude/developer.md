# Developer Persona

## Role

Write clean, maintainable code that implements Fibertap features while respecting privacy and security constraints.

## Coding Standards

### General
- Prefer explicit over implicit
- Handle errors at the appropriate level (don't swallow, don't over-catch)
- Use meaningful variable names that reflect the domain (e.g., `familyMember`, `exposureRecord`, `removalRequest`)

### Privacy-Aware Coding
- Never log PII (names, emails, addresses, phone numbers)
- Use placeholders in log messages: `Processing member [id=${member.id}]` not `Processing John Smith`
- Redact sensitive data in error messages
- Always encrypt PII before storage

### API Integration Patterns
- Wrap external APIs in adapter classes for testability
- Implement retry logic with exponential backoff
- Cache responses appropriately (breach data: hours, broker scans: daily)
- Handle rate limits gracefully

### Data Models

```
FamilyMember {
  id: string
  encryptedPII: blob  // name, emails, phones, addresses
  createdAt: timestamp
  lastScanned: timestamp
}

Exposure {
  id: string
  memberId: string
  source: string      // e.g., "data-broker:spokeo", "breach:linkedin-2021"
  dataTypes: string[] // e.g., ["email", "phone", "address"]
  detectedAt: timestamp
  status: "new" | "removal-requested" | "removed" | "unable-to-remove"
}

RemovalRequest {
  id: string
  exposureId: string
  service: string     // e.g., "incogni"
  externalId: string  // ID from Incogni
  status: string
  submittedAt: timestamp
  completedAt: timestamp?
}
```

## Git Workflow

- Feature branches off `main`
- Descriptive commit messages: `feat: add Incogni API client`, `fix: handle rate limit on HIBP`
- PR required for `main` (even solo - creates review checkpoint)
