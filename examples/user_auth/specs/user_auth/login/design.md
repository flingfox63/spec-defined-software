---
capability_id: user_auth.login
status: accepted
version: 1.1.0
---

# Technical Design: User Authentication Login

This design maps the pure business requirements of `spec.md` to concrete technical payloads, protocols, and APIs.

## 1. Interface & API Contracts

### Request Payload (JSON over POST)
```typescript
interface LoginRequest {
  username: string; // alphanumeric or email, length 3-64
  password: string; // cleartext password, length 8-128
}
```

### Response Payload (HTTP 200 Success)
```typescript
interface LoginSuccessResponse {
  success: true;
  token: string;      // Signed JWT token
  expires_in: number; // Token lifetime in seconds (e.g. 3600)
}
```

### Response Payload (HTTP 401/403 Failure)
```typescript
interface LoginFailureResponse {
  success: false;
  error_code: "USER_NOT_FOUND" | "INVALID_CREDENTIALS" | "INVALID_PAYLOAD" | "ACCOUNT_SUSPENDED";
  message: string;
}
```

## 2. Cryptographic & Protocol Architecture
- **Password Verification**: Passwords are hashed and verified using SHA-256 (in this prototype) or Bcrypt (in production). Cleartext passwords must never be logged or stored.
- **Token Signing**: Issue JWTs signed with the HS256 algorithm. The token contains the standard claims (`sub` or `user_id`) and an expiration timestamp.

## 3. Account Eligibility Enforcement
- **Physical state**: Each user record exposes a `status` value of `active` or `suspended`; legacy records without a value are treated as active in this prototype.
- **Decision order**: Verify credentials first, then reject a suspended account before token construction and outbound success auditing.
- **Failure mapping**: Return HTTP 403 with `ACCOUNT_SUSPENDED`; omit token fields from the response.

## 4. Integration & Outbound Side Effects
- **External Audit Endpoint**: On login success, post JSON security audit logs to:
  `https://auth-audit.example.com`
- **Resilience Policy**: If the outbound audit call fails, log a local warning but still allow the login process to complete successfully (no cascading failures).
- **Suspension boundary**: Do not invoke the successful-login audit endpoint when account eligibility denies the login.
