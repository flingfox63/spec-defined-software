# Specification & Design Blueprints

Use these standard templates as your starting point when creating new capabilities.

---

## 1. Spec Template (`spec.md`)

```markdown
---
capability_id: <module_name>.<capability_name>
status: defined  # options: defined, implemented, deprecated
version: 1.0.0
side_effects:
  database:
    - table: "<table_name>"
      operations: ["select", "insert"]
  external_apis: []
  file_system: []
  browser_storage: []
---

# Capability Specification: <Capability Name>

## 1. Purpose
State the business value, context, and target user of this capability.

## 2. Acceptance Criteria
Describe the business behavior in Given/When/Then atomic criteria.
* **AC-1**: Given a valid user session, When the user triggers ... Then ...
* **AC-2**: ...

## 3. Interface / Contract
Describe inputs and outputs conceptually (use plain domain terms, no physical keys or datatypes).
* **Inputs**: User credentials, target session token.
* **Outputs**: Verification status, profile payload.

## 4. Business Rules & Edge Cases
Describe core constraints, error thresholds, and retention limits.
```

---

## 2. Technical Design Template (`design.md`)

```markdown
# Technical Design: <Capability Name>

## 1. Architectural & Protocol Overview
Define communication protocols, entryways, and topology.

## 2. Business Contract Mapping
Map the spec's conceptual inputs/outputs to physical API JSON keys or parameters.

| Spec Concept | Physical Key / Header | Data Type | Notes |
| :--- | :--- | :--- | :--- |
| User credentials | `body.auth.username` | String | Must be sanitized |

## 3. Database Schema & Data Model
Define table names, indices, and exact columns.

## 4. Detailed API & Class Design
Endpoints, controllers, services, repositories, and caching.

## 5. Data Transition & Migration Design
Define DB migration script ordering, schema compatibility, and rollback SQL queries.
```
