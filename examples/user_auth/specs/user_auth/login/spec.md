---
capability_id: user_auth.login
status: implemented
version: 1.0.0
side_effects:
  database:
    - table: "users"
      operations: ["select"]
  external_apis:
    - domain: "auth-audit.example.com"
      purpose: "Send authentication logs for security compliance audits"
---

# Capability: User Authentication Login

## Purpose
Authenticate users securely using their username and password. On successful verification, issue a signed token and log a security audit entry to an external audit endpoint.

## Acceptance Criteria
- **AC-1**: If the username does not exist in the database, return an authentication error (HTTP 401) with code `USER_NOT_FOUND`.
- **AC-2**: If the password does not match the stored hash, return an authentication error (HTTP 401) with code `INVALID_CREDENTIALS`.
- **AC-3**: On successful verification, issue a JWT token signed with HS256 containing `user_id` and an expiration timestamp.
- **AC-4**: On successful login, trigger a secure HTTPS request to `auth-audit.example.com` to log the audit trail.

## Interface / Contract

### Request Contract
```typescript
interface LoginRequest {
  username: string; // alphanumeric or email, length 3-64
  password: string; // cleartext password, length 8-128
}
```

### Response Contract (Success)
```typescript
interface LoginSuccessResponse {
  success: true;
  token: string;      // Signed JWT token
  expires_in: number; // Token lifetime in seconds (e.g. 3600)
}
```

### Response Contract (Failure)
```typescript
interface LoginFailureResponse {
  success: false;
  error_code: "USER_NOT_FOUND" | "INVALID_CREDENTIALS" | "INVALID_PAYLOAD";
  message: string;
}
```

## Business Rules & Edge Cases
- **Password Hashing**: Only verify against SHA-256 (for this example, or bcrypt in production). Do not store or process cleartext passwords in memory.
- **Audit Failure Resilience**: If the audit call to `auth-audit.example.com` fails, the login should still succeed but log a local warning (no cascading failure).

## Technical Notes
- The runnable example generates a process-local signing key and contains no committed credential. Production implementations must load a stable signing key from a protected deployment configuration or secret store.
