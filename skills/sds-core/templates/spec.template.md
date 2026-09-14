---
capability_id: <module>.<capability_name>
status: defined  # options: defined, implemented, deprecated
version: 1.0.0
ac_derivation:
  AC-1:
    scenario: ../_context/user-journey.md
    reasoning: "<Explain why this outcome follows from the actor, initial state and goal>"
    ambiguity: "<Record the chosen interpretation and rejected alternative, or none>"
    validation: "<State a positive outcome and a boundary or counterexample outcome>"
  AC-2:
    scenario: ../_context/user-journey.md
    reasoning: "<Explain why this outcome follows from the actor, initial state and goal>"
    ambiguity: "<Record the chosen interpretation and rejected alternative, or none>"
    validation: "<State a positive outcome and a boundary or counterexample outcome>"
  AC-3:
    scenario: ../_context/user-journey.md
    reasoning: "<Explain why this outcome follows from the actor, initial state and goal>"
    ambiguity: "<Record the chosen interpretation and rejected alternative, or none>"
    validation: "<State a positive outcome and a boundary or counterexample outcome>"
---

# Capability Specification: <Capability Name>

## 1. Purpose
Identify the actor, initial business state, goal and observable outcome from accepted `_context/`. A concise statement of the business goal. Explain what problem this capability solves for the user, and why it is necessary.

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

## Authoring check
For every AC, complete `ac_derivation` above using business language and an
existing durable context path (optionally a heading anchor). Compare plausible
interpretations against the scenario. If the context cannot choose between
materially different outcomes, ask the user and block the dependent work.
Do not fill accepted reasoning from the current code or leave placeholder text.

Example business AC: Given an unpaid order / When the buyer cancels / Then the
order is cancelled and no payment is collected. Locking, transaction boundaries,
endpoint names, JSON keys and table columns belong in `design.md`. User-visible
compatibility or performance promises remain business requirements when needed.
Never reference temporary review artifacts; promote accepted conclusions here.
