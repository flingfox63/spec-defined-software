# User Auth Context — User Journey & Domain Model

## System Overview

This module handles secure user authentication, token issuance, and password verification.

## Core User Journey

1. **User Login**:
   - Given a registered user with valid credentials.
   - When the user submits their username and password.
   - Unknown usernames and incorrect passwords are denied with their corresponding business reason.
   - Successful login requests a security audit record.
   - Then the system verifies the password and, when the account is active, issues a secure signed token.
   - If the account is suspended, the system denies login without issuing a token or recording a successful-login audit entry.
2. **Accessing Protected Resources**:
   - The user includes the JWT token in their request header.
   - The system validates the signature, expiration, and payload, granting or denying access.

## Domain Models

- **User**:
  - `id`: unique string uuid
  - `username`: unique email or alphanumeric handle
  - `password_hash`: secure password hash
  - `status`: account eligibility state; an active account may log in, while a suspended account may not
- **AuthToken**:
  - `access_token`: signed JWT string
  - `expires_at`: Unix timestamp of token expiry
