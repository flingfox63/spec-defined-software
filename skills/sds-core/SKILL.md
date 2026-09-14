---
name: sds
description: "Apply Spec-Defined Software (SDS) to software changes, audits, refactors, frontend/backend work, database migrations, release automation, and spec/code alignment. Use when a project has specs/, .sds.harness.yaml, or asks for spec-first delivery, zero-drift verification, technical assessment placement, pre-release checks, or SDS self-check maintenance."
metadata:
  version: "1.2.2"
---

# SDS — Spec-Defined Software (Requirement Delivery Version)

Treat the durable specification as the highest source of truth for requirement delivery. Work in this order:

`user scenario -> accepted context/spec/design -> implementation -> verification -> requirement delivery`

## SDS Philosophy: The Ultimate Destination
Spec-Defined Software (SDS) represents the transition of requirement delivery from manual coding to precise specification-defining. In this ultimate paradigm, a business requirement's complete behavioral and business identity is codified in its `_context/` and `spec.md` (the "What"). The technical designs, code implementation, and test suites are logical derivatives that can be automatically synthesized, verified, and healed (e.g., by AI engines). 

**Philosophical Directive for the Agent**: Always treat the Specification as the absolute source of truth for the entire requirement delivery process. Prioritize the completeness and clarity of the Specification over immediate coding. The code is merely a compiled artifact of the delivered requirement. Keep your edits highly focused on the Spec-first delivery model, mapping every change back to an Acceptance Criterion (AC) in the Spec.

## Core Concepts for Beginners
To avoid any confusion when starting with SDS, remember these three core separations:
1. **Module vs. Capability (and why Capability $\neq$ API Interface)**:
   - **Module** (Business Subdomain): A high-level, stable noun representing a macro business area (e.g., `order`, `billing`, `user_auth`).
   - **Capability** (User Feature Scenario): A specific, actionable business transaction/lifecycle inside a Module (e.g., `place_payment_order`, `refund_payment`).
   - **The Golden Rule**: **A Capability is NOT a physical API interface/endpoint.** A Capability represents business-value scenarios from the user/product perspective (defined in `spec.md`). A single Capability (like `place_payment_order`) can be physically realized by multiple API endpoints (e.g., separate redirect vs direct-debit endpoints) or polymorphic parameter routes, which are mapped solely in `design.md`. 1-to-1 mapping of APIs to Capabilities is a strict anti-pattern that leads to information duplication and spec fragmentation.
2. **`specs/` (Durable) vs. `specs_review/` (Temporary)**:
   - **`specs_review/`** is the **Drafting Kitchen** (local, gitignored). Write research, feature proposals, design comparisons, and execution plans here.
   - **`specs/`** is the **Authoritative Dining Room** (tracked in git). Once a proposal is accepted, promote only the final agreed-upon conclusions into `specs/` as `spec.md` and `design.md`. Implementation code must ONLY be written based on accepted specs.
3. **Where does the Code live?**:
   - SDS files live *alongside* your source code as a metadata sidecar.
   - Your actual implementation code (Python, Go, JS, etc.) lives in your standard project folders (e.g., `src/`, `app/`), and automated test files live in `tests/`, completely separate from the `specs/` directory.

## User Scenario Translation Guidelines

When given a raw User Scenario (e.g., qualitative user requests or behavioral needs), the Agent must translate it into an authoritative specification using these guidelines:
1. **Distill the Core Business Value**: Extract the specific problem being solved, the target user, and the desired outcome. Avoid technical solutioning at this stage.
2. **Determine Bounded Context Routing**: Route the scenario to the correct Module (bounded context) using the global `system-blueprint.md`. Do not let physical code structures dictate business boundaries.
3. **Formulate Gherkin-Style Acceptance Criteria**: Translate the user scenario into precise, atomic, and verifiable Acceptance Criteria (ACs) using the `Given-When-Then` format. Ensure ACs cover both the happy path and critical business boundaries (e.g., data compliance, error state constraints, and user experience thresholds).
4. **Draft Conceptual Interface Contracts**: Extract the conceptual elements that must flow in and out of the capability (e.g., "User credentials", "Validation status") as defined by the scenario. Never use physical keys, physical endpoints, or camelCase terminology here.
5. **Enforce Local Invariants**: Identify and document any business rules or invariants that must remain unbroken (e.g., "A user cannot login if their account status is suspended").

## Per-AC scenario derivation gate

For EVERY AC (including errors, permissions, retries and recovery), record an
`ac_derivation` frontmatter entry in spec.md with `scenario`, `reasoning`,
`ambiguity`, and `validation`. The scenario is a relative existing Markdown path
under durable `_context/` (optional heading fragment). Record business reasoning,
the selected interpretation and why alternatives contradict the actor's goal or
state; use `none` only after checking for ambiguity. Validation states observable
positive and counterexample outcomes, not implementation-derived assertions.
Unresolved material choices block dependent implementation; ask only for those
choices and continue independent work. Never infer intended behavior from code.

The default `sds check` gate checks 100% record coverage, valid context references
and resolved non-placeholder fields for all ACs. It does NOT prove prose is true.
Perform a separate spec-only pass: reconstruct each scenario, challenge the chosen
interpretation with a counterexample, and verify the outcome against context.
Record accepted conclusions in spec/context and temporary review evidence in the
review workspace. For each AC, design.md maps the technical mechanism to positive
and boundary tests. Revisit all affected derivations when context or ACs change.

## Business specification and technical design

Write spec.md for the actor/product reader: goals, business state transitions,
observable outcomes, concepts, constraints and failure meaning. Write design.md
for the implementer: protocols, physical fields, classes, schema, concurrency,
retries and verification mapping. Example: "Cancellation prevents collection on
an unpaid order" belongs in spec; "compare-and-set the payment state inside a
transaction" belongs in design. Keep user-visible compatibility and performance
promises in spec when they are actual requirements. Mark inapplicable design
sections with a reason instead of inventing technical infrastructure.

Durable documents must be self-contained: no inline links, reference links, HTML,
bare paths, escaped paths or code references to temporary review artifacts.
Promote the accepted conclusion and cite durable context instead.

## Start every task

1. Read the repository instructions (`AGENTS.md` or equivalent), `.sds.harness.yaml`, relevant `_context/`, capability `spec.md`, and accepted `design.md`.
2. Route the change by the user scenario and ownership boundary, not by the table, implementation file, or current directory. Confirm the capability lives under the owning module, its `capability_id` matches that path, and the module has `_context/`. Put cross-cutting schema/migration/infrastructure design work under a system/ops module.
   - **System Blueprint & Blurry Boundaries**: The `system-blueprint.md` is a guiding structural map, not a rigid blocker. If it is missing, empty, or placeholder-only (such as in newly initialized projects), the Agent must infer module boundaries based on standard domain-driven design (DDD) nouns or scaffolded folders. If a requested capability crosses multiple module domains, or if its ownership boundaries are blurry, the Agent **MUST NOT make arbitrary architectural assumptions**. It must outline the alternative module placements to the human user in the chat, explain the pros/cons of each, and **stop to ask the user to decide** the capability's ownership boundary.
3. Classify the request before writing documents:
   - assessment, comparison, audit, proposal, migration plan, execution plan, diagnostics, or test evidence -> `specs_review/`;
   - accepted current behavior/contract (100% Product-Oriented) -> `spec.md`;
   - accepted implementation architecture (100% Tech-Oriented) -> `design.md`;
   - accepted cross-capability facts, scenarios, boundaries, vocabulary, or factual history -> `_context/`.
4. If the user accepts a proposal and asks to implement it, promote only the accepted decisions into durable specs/design/context before changing code. Keep the original assessment in `specs_review/`.
5. Never link durable files under `specs/` to gitignored `specs_review/` artifacts.

SDS does not impose a plan-first or confirmation-first gate. Create a plan when complexity or repository policy requires one, and request confirmation only when intent, authority, or a material product decision is unresolved.

### Process Intensity & Complexity Thresholds

To prevent both over-engineering on simple fixes and reckless spec-skipping on material modifications, the Agent must classify tasks and apply the following quantified thresholds based on estimated effort (Person-Days / 人天):

1. **Ultra-Lightweight Changes (< 0.5 Person-Days / Simple Typos or Logging Tweaks)**:
   - *Guideline*: If a task is extremely simple (e.g., fixing a typo, correcting a localized UI margin/label, or adjusting a minor log format string) and does not change any business outcomes, user scenarios, or database schemas.
   - *Action*: The Agent may directly modify the implementation and test files, adding or updating the `@sds-trace` comments, and bypass full `spec.md` or `design.md` creation/modification.
2. **Minor Modifications (0.5 to 1.5 Person-Days / Single-Endpoint or Field Adjustments)**:
   - *Guideline*: If a task involves a minor behavior change (e.g., adding an optional field to an existing API, modifying a simple validation rule, or adding a small UI behavior) but does not alter macro architectures.
   - *Action*: The Agent **MUST** update `spec.md` and `design.md`. However, to maintain velocity, the Agent may write directly to `specs/` (authoritative) and proceed straight to implementation and testing, skipping the complex `specs_review/` draft-and-promotion phase.
3. **Major Features & Material Architectural Alterations (> 1.5 Person-Days / New Endpoints or Schema Migrations)**:
   - *Guideline*: If a task represents a new capability, a database schema migration, a new API endpoint, or an integration that alters state transitions or core business flows.
   - *Action*: The Agent **MUST** follow the rigid, full-lifecycle SDS delivery workflow (Stage 1 Draft in `specs_review/` -> Present to User for Acceptance -> Promote to `specs/` -> Implement -> Trace -> Verify).

* **The Golden Fallback**: If the complexity tier or estimated person-days are ambiguous, or if you are unsure whether a spec update is required, you **MUST stop and ask the user to clarify the desired process intensity** before touching any file.

### Priority of Overlapping Guidelines & Overrides

When overlapping instructions exist (e.g., `SKILL.md` vs. local `AGENTS.md` or `.sds.harness.yaml`):
1. **Local project-defined configurations (`.sds.harness.yaml`) and local `AGENTS.md` always take ultimate precedence**, as they contain the authoritative business domain boundaries, specific constraints, and local project conventions.
2. If any rule in `SKILL.md` conflicts with a local project's rule, the Agent must adhere to the local project's rules, and **must ask the user for confirmation** if the conflict introduces logical risk.

## Key Project File Constraints & Governance

To prevent information conflicts and keep the repository clean, the SDS layout has strict key file constraints. Any files outside this list under `specs/` are considered redundant and must be actively flagged, pruned, or consolidated.

1. **Under Global Context `specs/_context/` (System-Wide, Allowed Files)**:
   - `system-blueprint.md`: Global system architecture concepts, system module boundaries, and cross-module integration mapping (Context Mapping). No local module entities here.
   - `glossary.md`: Global, system-wide unified dictionary and business terms.
   - `change-history.md`: Overall factual migration timeline and historical change facts.
   *(Alternatively, a single `README.md` is allowed to unify these for small projects).*

2. **Under Module-Level Context `specs/<module>/_context/` (Highly Cohesive, Allowed Files)**:
   - `glossary.md`: Module-specific local business terms and dictionary.
   - `domain-model.md`: Module-specific local business entities, concepts, and domain relationships (Aggregate Roots and Entity graphs).
   - `user-journey.md` / `business-flow.md`: Bounded context boundaries, local invariants, and business rules specific to this module.
   - `change-history.md`: Factual migration timeline and history specific to this module.
   *(Alternatively, a single `README.md` is allowed to unify these for small/medium modules. Do NOT allow ad-hoc markdown files).*

3. **Under Capability-Level `specs/<module>/<capability>/` (Allowed Files)**:
   - Exactly `spec.md` (accepted business behavior and AC, 100% product-oriented).
   - Exactly `design.md` (accepted technical implementation, 100% tech-oriented).
   - *No other files allowed here.* Any temporary thoughts, scratchpads, or research must be in `specs_review/`.

4. **Active Governance & Escalation Boundary**:
   - When the agent performs any task, it MUST inspect the `specs/` directory.
   - If any unauthorized or ad-hoc markdown files are found (e.g., legacy specs, raw notes, or duplicated doc files), the agent's behavior depends on the task mode:
     - **In Implementation / Development Mode**: The Agent must immediately flag them to the user, recommend their removal/consolidation, and merge their valid durable conclusions into the standard files above.
     - **In Pure Review / Audit / Diagnose Mode**: The Agent **MUST NOT** perform any physical merges or modifications under `specs/` or source folders. It must ONLY flag the issue to the user, propose concrete consolidation recommendations in the chat or diagnostics file, and **stop to ask for explicit user permission** before performing any physical file write or merge.
     - **When in Doubt**: If the task mode or boundaries are ambiguous, the Agent **MUST stop and ask the user for confirmation** rather than arbitrarily executing write operations.

5. **Durable Test Code vs. Verification Evidence**:
   - **Durable Test Code**: All long-term automated test suites (pytest, Jest, unit/integration scripts) must live in the standard physical repository directories (e.g., `tests/` or `<module>/tests/`). They are first-class code assets and must use tracing annotations (`@sds-trace: <capability_id>:AC-n`) to trace back to the spec.
   - **Verification Evidence**: The folder `specs_review/<module>/<capability>/verification/` is strictly a gitignored, temporary staging area. It only stores ephemeral run logs, test results, local screenshots, and validation outputs. No durable test scripts may be written or maintained here.

## Define the complete change surface

Do not limit SDS to application endpoints. Treat these as requirement deliverables when they change:

- browser and mobile interaction, responsive layouts, navigation, accessibility, and source/build-output boundaries;
- API payloads, identity propagation, authorization, data scopes, and error behavior;
- database schema evolution, migration ordering, compatibility, failure recovery, and migration ledger state;
- lifecycle reachability from empty/initial states, state transitions, scheduled completion, retry/backfill, and reconciliation;
- authoritative data stores, single-writer boundaries, materialization order, and compatibility projections/exports.

Update the owning capability spec first. Record implementation choices in `design.md`, not in acceptance criteria. Create or extend a system/ops capability when cross-cutting data transitions have no existing owner.

## Implement and verify

1. Make the smallest implementation that satisfies the accepted spec.
2. Add `@sds-trace: <capability_id>:AC-n` to trace every single defined Acceptance Criterion (`AC-n`) in implementation code and test classes.
   - **Trace Coverage Standard**: For any capability marked with `status: implemented` or `status: verified`, 100% of its ACs must have matching `@sds-trace` annotations. The check engine strictly enforces this coverage standard; any missing trace annotation will fail the build.
3. Derive tests from the spec, not from the implementation. Use an independent agent only when the user or repository rules permit delegation; otherwise perform a separate spec-only test-design pass.
4. Cover happy paths, authorization/data boundaries, invalid input, dependency failure, and retry/recovery where applicable.
5. Run and validate the project-level self-checker: As an AI Agent, you must execute the central `sds check` command in the background to ensure zero-drift, check traceability annotations, and validate directory compliance. If validation fails, parse `specs_review/diagnostics.json`, fix the target files, and rerun.
6. Run every project verification command declared in `.sds.harness.yaml`. Verify that your code changes pass all linting, static analysis, and automated test suites before delivering the requirement.
7. Before handoff, inspect the complete diff and working tree for stale files, generated artifacts in source directories, obsolete legacy entrypoints, untracked files, and spec/code drift. Do not present or commit the work unless all checks return 100% success.

## Multi-Agent Orchestration & Compatibility

To maximize delivery quality and reduce cognitive load, SDS remains fully compatible with multi-agent orchestration paradigms and agentic skills frameworks (e.g., Jesse Vincent's `obra/superpowers`). When integrated into an agentic execution host, the Agent is encouraged to coordinate tasks using specialized subagents:
- Use **Socratic Brainstorming** to translate raw User Scenarios into Gherkin-style Acceptance Criteria (ACs) in `specs_review/`.
- Use **Defensive Planning** to break down accepted technical designs (`design.md`) into file-specific execution plans.
- Use **Subagent-Driven Development (SDD)** to spawn isolated subagents for implementing physical codes and tests, ensuring clean context boundaries.
- Use **Verification-Before-Completion** loops to execute `sds check` and project-level test commands, validating zero-drift.

## Artifact locations

```text
project/
├── src/                                  # Your actual implementation source code
│   └── <module>/                         # Project-specific physical package/code
├── tests/                                # Your durable automated test suites (with @sds-trace)
├── .sds.harness.yaml
├── specs/                                # AUTHORITATIVE CONTRACTS (Tracked in Git)
│   ├── _context/                         # Global context
│   │   ├── system-blueprint.md
│   │   ├── glossary.md
│   │   └── change-history.md
│   └── <module>/
│       ├── _context/                     # Module context
│       │   ├── glossary.md
│       │   ├── domain-model.md
│       │   ├── user-journey.md
│       │   ├── business-flow.md
│       │   └── change-history.md
│       └── <capability>/
│           ├── spec.md                   # accepted What (100% Product-Oriented)
│           └── design.md                 # accepted How (100% Tech-Oriented)
└── specs_review/                         # TEMPORARY REVIEW WORKSPACE (Gitignored)
    └── <module>/<capability>/
        ├── assessment.md
        ├── plan.md
        ├── task.md
        ├── diagnostics.json
        └── verification/                 # temporary evidence, screenshots, logs (no durable test code)
```

The centralized `sds-cli` tool provides standard global `sds check` and `sds init` capabilities. Projects do not need to copy `sds_self_check.py` into their root folder; they only require `.sds.harness.yaml` and the `specs/` folder tree, executing validation globally via `sds check`.

## Capability spec minimum (100% Product-Oriented)

Every `spec.md` must contain:
- `Purpose`: Concise business goal.
- `Acceptance criteria`: Atomic, verifiable business conditions using plain domain terms (Given/When/Then).
- `Conceptual Interface Contract`: Input and output business information exchange elements (no physical API protocols, JSON fields, or camelCase keys).
- `Business Rules & Edge Cases`: Constraints and error behaviors described from the user's/business's perspective. This includes business-level experience thresholds, data compliance retention, and core business limits.
- Declared business-level side effects where relevant.

## Technical Design minimum (100% Tech-Oriented)

Every `design.md` must contain:
- `Architectural & Protocol Overview`: Protocols, gateways, and topology.
- `Business Contract Mapping`: A mapping table translating `spec.md`'s conceptual inputs/outputs to physical API fields, JSON keys, headers, or query params.
- `Database Schema & Data Model`: Exact table names, column types, and indices (no physical schemas in spec.md).
- `Detailed API & Class Design`: API endpoints, controllers, services, repositories, and cache strategies.
- `Data Transition & Migration Design`: Local database migrations, schema version history, backward compatibility mapping, and local rollback SQL scripts (no server deployment steps). This includes technical mechanisms (caching, indexes, queues) used to satisfy the spec's business non-functional budgets.

## Safety Guidelines for Read-Only Review Tasks

When tasked with a pure "review", "audit", "diagnose", or "check" assignment, the Agent MUST NOT modify any source code, specifications, or configurations under `specs/` or project folders. 
- **The Safe Boundary**: In pure review modes, the Agent is strictly a diagnostic tool. It must only run the linter and write findings into `specs_review/diagnostics.json` or present structured reports in chat.
- **The Modification Boundary**: Code, spec, or design file additions, deletions, or auto-healing refactors are ONLY permitted when the user explicitly requests implementation, auto-healing, or development work.

## References

- Read `references/sds-workflow.md` for the detailed lifecycle and verification model.
- Read `references/sds-playbook.md` when initializing or upgrading a project.
- Use `templates/spec.template.md`, `templates/design.template.md`, and `templates/harness.yaml` as starting points.
- Use the globally packaged `sds check` command for cross-platform baseline validation and zero-drift checks.

### Derivation policy migration
New scaffolds explicitly enable `enforce_ac_derivation: true`. Existing projects
missing this key retain previous checks and receive one migration warning per
run. Backfill every AC from accepted context before enabling the gate. Explicit
false skips it with one warning. A skipped gate never proves scenario alignment;
the per-AC authoring and semantic review requirements still apply.
