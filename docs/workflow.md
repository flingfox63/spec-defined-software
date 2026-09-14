# The SDS Delivery Workflow

SDS treats durable specification as the highest source of truth. Every requirement delivery goes through a structured, 5-stage lifecycle.

---

## The 5-Stage Life-Cycle

```text
[ Concept & Scenarios ] ➔ [ Spec & Design Contract ] ➔ [ Implementation ] ➔ [ Zero-Drift Verification ] ➔ [ Release ]
```

### Stage 1: Translate User Scenarios
Fuzzy, qualitative requests must be distilled into concrete business value and mapped to standard Gherkin-style **Acceptance Criteria (ACs)**:
* **Given**: The pre-existing state of the system or context.
* **When**: The action or transaction triggered by the user.
* **Then**: The observable outcome, state transitions, or side effects.

For every AC, record `ac_derivation` in spec frontmatter: `scenario` points to
an existing durable `_context/` Markdown document; `reasoning` explains the
inference from the actor, initial state and goal; `ambiguity` records the accepted
interpretation and rejected alternative (or `none` after review); `validation`
states positive and counterexample business outcomes. Material ambiguity that
context cannot resolve requires user input before dependent implementation.
See the [authoring templates](reference/templates.md).

### Stage 2: Draft Contracts & Human Acceptance
* **The Drafting Kitchen**: Conceptual specifications and technical designs are initially drafted as proposals inside `specs_review/` (a temporary, gitignored scratch directory).
* **The Acceptance Gate**: A specification is officially **Accepted** once the human user/product manager explicitly approves the draft. Upon acceptance, promote only the agreed conclusions into authoritative, git-tracked `spec.md` and `design.md`; keep original review notes in the temporary workspace. Never reference those temporary artifacts from durable documents, including through reference links, HTML, bare paths or escaped paths.
* **The Division of Labor**:
  * Product-oriented inputs/outputs must be declared conceptually in `spec.md` (no physical camelCase keys, ports, or protocol details).
  * Technical details, mappings, database schemas, API structures, and indexes must be declared separately in `design.md`.

### Stage 3: Implement & Trace
When writing physical code or tests, developers (or AI subagents) must place traceability comments linking back to specific spec ACs:

```python
# @sds-trace: user_auth.login:AC-1
def authenticate_user(credentials):
    ...
```

This establishes identifier traceability. For implemented or verified capabilities, the harness requires a matching annotation for every AC, but does not prove separate implementation and test coverage or semantic correctness. Derive tests in a separate context-and-spec-only pass before inspecting code; map every AC to a technical mechanism, positive test and boundary/counterexample test in design.

### Stage 4: Verify Zero-Drift
Before pushing any code, run the self-checker:
```bash
sds check
```
The check engine scans:
* **Directory structure compliance**: Ensure files are in standard directories.
* **Spec-to-Code Drift**: Flags guarded implementation changes without a spec change in the change set. This coarse check does not prove that the changed spec is the correct one.
* **Trace matches**: Validates capability/AC identifiers and requires every AC in implemented or verified capabilities to have a matching annotation.
* **Scenario derivation**: When explicitly enabled, checks every AC regardless of status for a complete derivation record and a valid durable context source. Missing records, explicit unresolved markers and placeholders fail.
* **Durable references**: Rejects dependencies on temporary review artifacts.
* **Project verification**: Runs commands configured in `.sds.harness.yaml` after baseline checks pass.

An independent semantic review must challenge every AC against its source
scenario. A complete derivation record does not prove that its reasoning is true.
Existing projects backfill all AC records before explicitly enabling the gate; `enforce_ac_derivation: false`
is an explicit temporary migration escape hatch, reported as skipped verification.

### Stage 5: Release Guard (Ops)
> [!NOTE]
> *This stage is designed to be automated by the upcoming `sds-ops` skill (currently in **Planned** status).*
> *本阶段旨在由未来的 `sds-ops` 智能体技能包自动化执行（目前处于 **规划中** 状态）。*

Deployments must execute Capistrano-style atomic symlink releases. 
1. Build code and assets.
2. Execute local database migrations.
3. Validate and confirm zero-drift.
4. Shift the active symlink to point to the new release directory.
5. In case of verification failure, instantly rollback the symlink to the previous stable release.
