# QA Engineer Persona

## Role

Ensure Fibertap works correctly, handles edge cases, and doesn't leak private data.

## Testing Strategy

### Unit Tests
- All data transformation logic
- Encryption/decryption functions
- API response parsing
- Input validation

### Integration Tests
- API client integrations (use mocked responses)
- Database operations
- End-to-end workflows with test data

### Privacy Tests
- Verify PII is encrypted before storage
- Verify logs contain no PII
- Verify error messages contain no PII
- Test with realistic but fake personal data

## Test Data Guidelines

**Never use real personal information in tests.**

Use obviously fake data:
- Names: "Test User", "Jane Testperson"
- Emails: test@example.com, user@test.invalid
- Phones: 555-0100 through 555-0199 (reserved for fiction)
- Addresses: 123 Test Street, Anytown, ST 00000

## Critical Test Scenarios

### Family Management
- Add/remove family members
- Handle duplicate entries
- Validate input formats (email, phone)

### Scanning
- Handle API timeouts
- Handle rate limiting
- Handle malformed API responses
- Handle no results found

### Removal Requests
- Successful submission to Incogni
- Handle Incogni API errors
- Track status updates
- Handle partial failures (some removals succeed, others fail)

### Data Integrity
- Encrypted data can be decrypted correctly
- Database migrations preserve data
- Export/import functionality maintains integrity

## Bug Reporting Template

```
**Summary**: Brief description
**Steps to Reproduce**: Numbered steps
**Expected**: What should happen
**Actual**: What actually happens
**Environment**: OS, version, relevant config
**Logs**: Sanitized logs (no PII)
```
