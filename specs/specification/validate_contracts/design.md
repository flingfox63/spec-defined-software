---
sds_kind: authoritative-design
capability_id: specification.validate_contracts
status: accepted
---

# Contract validation design

## Architectural & Protocol Overview
The standard-library harness validates durable Markdown before running project
verification. The packaged Skill, templates and initializer share authoring rules.

## Business Contract Mapping
Each spec frontmatter contains `ac_derivation`, keyed by exact AC identifier.
Each record contains nonempty strings: `scenario` (relative existing Markdown
file under durable `_context/`, optionally a heading fragment), `reasoning`,
`ambiguity` (resolved decision with justification or `none`), and `validation`
(business positive/negative expectations). Placeholder or unresolved values fail.
`enforce_ac_derivation` is explicitly true in new scaffolds. A missing key uses
compatibility mode and emits one migration warning; false emits one skip warning.
Neither skipped mode is semantic verification. Refresh never silently enables it.

## Detailed API & Class Design
- AC-1: Normalize Markdown escapes, URL encoding and path separators; detect
  review artifact paths in inline, reference, HTML, bare and code notation.
  Resolve local Markdown/HTML targets to catch symlink and relative aliases.
- AC-2: Compare all extracted ACs with derivation keys; reject missing/extra
  records, invalid field types, placeholders and non-durable context sources.
  Validate optional heading anchors against the context document.
- AC-3: Templates require scenario-first business ACs and a design table mapping
  every AC to mechanism, positive test and counterexample. Skill guidance requires
  a separate spec-only test-design and semantic review pass.

## Verification Mapping
| AC | Implementation | Verification |
| --- | --- | --- |
| AC-1 | Durable reference scanner | Alternative notations, custom review directory, durable links and alias regressions |
| AC-2 | Derivation validator | Complete, missing, stale, unresolved and invalid-source records |
| AC-3 | Packaged templates and initializer | Generated templates include derivation and technical mapping guidance |

## Database Schema & Data Model
No database. Records are parsed by the existing small YAML parser.

## Data Transition & Migration Design
Existing projects backfill all AC derivations before explicitly enabling the gate.
No automatic generation of accepted reasoning from existing implementation.

## Review fixes
AC-1 matches the full root-relative review directory and resolves local link
aliases; bare paths and code references remain covered. AC-2 treats only a whole
angle-bracket value as a placeholder, preserving comparisons inside sentences.
AC-3 uses a complete illustrative cancellation scenario in newly initialized
projects, while reusable authoring templates retain placeholders and version 1.0.0.
Regression tests cover old/missing, partial and complete records across absent,
false and true policies; fresh init must pass check.
