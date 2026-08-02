---
capability_id: <module>.<capability_name>
status: defined  # options: defined, implemented, deprecated
version: 2.0.0
---

# Capability Specification: <Capability Name>

## 1. Purpose
A concise statement of the business goal. Explain what problem this capability solves for the user, and why it is necessary.

## 2. Acceptance Criteria
Provide a list of verifiable conditions. Keep them clear, atomic, and testable using plain business/domain terms:

- **AC-1**: Given [Precondition] / When [Action] / Then [Expected business outcome]
- **AC-2**: Given [Precondition] / When [Action] / Then [Expected business outcome]
- **AC-3**: Given [Precondition] / When [Action] / Then [Expected business outcome]

## 3. Interface / Contract
Define the conceptual information exchange required for this capability. Do not include physical API routes, JSON payloads, or specific database/code schemas.

### A. Business Inputs (Information required to initiate):
- **User Identifier**: The identity of the authenticated user performing the action.
- **Input Item 1**: Explanation of the required business input (e.g. quantity, selected ID).

### B. Business Outputs (Information returned upon completion):
- **Result Status**: Succession or failure of the action from a business perspective.
- **Output Item 1**: Explanation of the business output (e.g. generated order reference).

## 4. Business Rules & Edge Cases
Detailed business constraints, validation rules, and specific edge case behaviors from the user's perspective:

- **Validation Rules**: Minimum lengths, business constraints, valid formats.
- **Error Behavior**: Map specific failure scenarios to user-friendly business descriptions.
- **Rate Limits & Boundaries**: Max/min thresholds, business throttling policies.

## 5. Operational Contract (When Applicable)
Define business-level lifecycle operational goals (e.g., retention, compliance, auditing rules). Keep technical choices (e.g. database schema migrations, deployment scripts, cron setups) in `design.md`.
