---
capability_id: specification.validate_contracts
status: implemented
version: 1.0.0
ac_derivation:
  AC-1:
    scenario: ../_context/user-journey.md
    reasoning: Accepted requirements must survive deletion of temporary review notes.
    ambiguity: Directory vocabulary is permitted; references to temporary artifacts are not.
    validation: Reject temporary document references in all durable documents while allowing durable context references.
  AC-2:
    scenario: ../_context/user-journey.md
    reasoning: Every criterion needs a scenario basis to prevent an interpretation that contradicts user intent.
    ambiguity: Structural completeness does not prove semantic correctness; an independent scenario review remains required.
    validation: Reject missing criteria records, invalid context sources and unresolved interpretations; accept complete records for all criteria.
  AC-3:
    scenario: ../_context/user-journey.md
    reasoning: Business readers must understand outcomes without choosing an implementation technology.
    ambiguity: User-visible protocol requirements may be business constraints; internal mechanisms belong in technical design.
    validation: Generated guidance separates business outcomes from mechanisms and requires design and verification coverage for every criterion.
side_effects:
  database: []
  external_apis: []
  file_system:
    - Local validation diagnostics and generated authoring templates
---

# Validate durable requirements

## Purpose
Help requirement authors deliver self-contained business contracts whose
acceptance conditions follow from accepted user scenarios.

## Acceptance criteria
- **AC-1**: Given an accepted document / When its references are checked / Then temporary review artifact dependencies are rejected regardless of reference notation.
- **AC-2**: Given any defined acceptance criterion / When delivery readiness is checked / Then its durable scenario source, outcome reasoning, ambiguity disposition and business verification expectations are required; missing or unresolved records prevent readiness.
- **AC-3**: Given an author translating a user scenario / When authoring guidance is used / Then business goals and observable outcomes belong in the specification, while technical mechanisms and criterion-to-implementation verification mapping belong in design.

## Interface / contract
Inputs are accepted context, acceptance criteria, derivation records and design.
Outputs are actionable readiness findings and authoring guidance.

## Business Rules & Edge Cases
Every criterion is reviewed, including error, recovery and boundary conditions.
A structural check cannot establish that prose is truthful or logically sound.
An independent spec-only review must challenge interpretations with a negative
scenario before declaring delivery complete. Unresolved decisions block only
the dependent work. Directory names used as vocabulary are not dependencies.

## Upgrade and initialization compatibility
New projects enable derivation checks explicitly and start with a complete,
illustrative business scenario that passes structural checks without claiming
implementation is complete. Existing projects with no derivation policy retain
their earlier checks and receive one migration warning per run. Explicitly
disabling the check emits one warning; explicitly enabling it enforces every AC.
Normal business comparisons are not unresolved placeholders. Custom temporary
workspace paths are matched in full, not by a coincidental directory basename.
New capability templates begin at version 1.0.0.
