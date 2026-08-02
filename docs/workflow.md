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

### Stage 2: Draft Contracts & Human Acceptance
* **The Drafting Kitchen**: Conceptual specifications and technical designs are initially drafted as proposals inside `specs_review/` (a temporary, gitignored scratch directory).
* **The Acceptance Gate**: A specification is officially **Accepted** once the human user/product manager explicitly approves the draft. Upon acceptance, the files are promoted (moved) into the authoritative, git-tracked `specs/` directory as `spec.md` and `design.md`. 
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

This acts as a durable linkage. The validation harness parses these comments to ensure 100% specification test coverage.

### Stage 4: Verify Zero-Drift
Before pushing any code, run the self-checker:
```bash
sds check
```
The check engine scans:
* **Directory structure compliance**: Ensure files are in standard directories.
* **Spec-to-Code Drift**: Ensures that if a spec was changed, the code was changed, and vice versa. It prevents hidden, un-documented features.
* **Trace matches**: Ensures all ACs declared in `spec.md` have matching `@sds-trace` implementation and test annotations in the repository.

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
