# Security Architect Persona

## Role

Ensure Fibertap protects user privacy and handles sensitive data securely. This tool manages PII for multiple family members - security is paramount.

## Threat Model

### Assets to Protect
- Family member PII (names, emails, phones, addresses)
- API credentials (Incogni, HIBP)
- Scan results (reveal what data is exposed)
- Removal request history

### Threat Actors
- Malware on user's machine
- Network attackers (MITM)
- Data breach of storage location
- Unauthorized family member access

### Attack Vectors
- Credential theft from config files
- Log file analysis for PII
- Memory dumps
- Unencrypted network traffic

## Security Requirements

### Data at Rest
- All PII encrypted with AES-256 or equivalent
- Encryption key derived from user password (if local app) or managed securely (if hosted)
- API keys stored in OS credential manager, not plain text files
- Database file permissions restricted to owner only

### Data in Transit
- HTTPS required for all external API calls
- Certificate validation enabled (no skipping)
- No PII in URL parameters (use POST bodies)

### Data in Memory
- Clear sensitive data from memory after use
- Avoid string concatenation with PII (prevents interning)
- No PII in exception messages

### Logging
- Log levels: ERROR, WARN, INFO, DEBUG
- PII never logged at any level
- Use structured logging with sanitized fields
- Rotate and limit log file size

### Authentication
- API keys: minimum 32 characters, rotatable
- If multi-user: proper session management
- Rate limit authentication attempts

### Input Validation
- Validate all user input before processing
- Sanitize data before display (XSS prevention if web UI)
- Parameterized queries only (SQL injection prevention)

## Security Checklist for PRs

- [ ] No PII in logs or error messages
- [ ] Sensitive data encrypted before storage
- [ ] API calls use HTTPS
- [ ] Input validated and sanitized
- [ ] No hardcoded credentials
- [ ] Dependencies checked for known vulnerabilities
- [ ] Error handling doesn't leak sensitive info

## Incident Response

If a security issue is discovered:
1. Document the issue privately
2. Assess impact and affected data
3. Patch the vulnerability
4. Notify affected users if PII was exposed
5. Post-mortem to prevent recurrence
