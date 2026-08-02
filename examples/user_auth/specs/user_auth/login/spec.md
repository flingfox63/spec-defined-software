---
capability_id: user_auth.login
status: implemented
version: 1.1.0
---

# Capability: User Authentication Login

## Purpose
Authenticate users securely using their username and password. On successful verification, issue a secure signed token and log a security audit entry.

## Acceptance Criteria
- **AC-1**: If the username does not exist, return an authentication error indicating user not found.
- **AC-2**: If the password does not match, return an authentication error indicating invalid credentials.
- **AC-3**: On successful verification, issue a secure signed token containing the user identifier.
- **AC-4**: On successful login, trigger a security audit entry to the official audit system.
- **AC-5**: Given a suspended account with valid credentials, when the account holder attempts to log in, then deny access without issuing a token or recording a successful-login audit entry.

## Interface / Contract
- **Inputs**: User credentials (username, password).
- **Outputs**: Verification status and, when login succeeds, a signed token containing the user identifier; when login is denied, a stable business reason.

## Business Rules & Edge Cases
- **Suspended accounts**: Account suspension takes precedence over successful login after the submitted credentials have been verified.
- **Denied-login side effects**: A denied suspended-account attempt must not create artifacts that imply a successful login.
