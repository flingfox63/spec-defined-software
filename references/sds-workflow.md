# SDS Workflow Reference

## Contents

1. Source-of-truth model
2. Artifact promotion lifecycle
3. Scenario and capability coverage
4. Implementation and test discipline
5. Verification layers
6. Operations, migration, and release contracts
7. Harness responsibilities and limits
8. Completion checklist

## 1. Source-of-truth model

SDS organizes software knowledge into four layers:

```text
User scenarios and durable context
               ↓
Capability specs (accepted What)
               ↓
Technical designs (accepted How)
               ↓
Code, configuration, migrations, builds, and deployment scripts
```

The spec wins when implementation and accepted intent differ. If implementation reflects a newly accepted behavior, update the spec first and then reconcile code and tests.

SDS applies to the whole delivery system, not only business code. Frontend builds, environment loading, runtime selection, database migrations, release activation, rollback, permissions, retention, monitoring, and diagnostics are behavior when users or operators depend on them.

## 2. Artifact promotion lifecycle

Classify by decision state, not by technical topic:

| Artifact | Location | Tracked | Meaning |
|---|---|---:|---|
| Technical assessment, comparison, audit, proposal | `specs_review/` | No | Reasoning in progress |
| Execution plan, task state, diagnostics, logs, screenshots | `specs_review/` | No | Local process/evidence |
| Accepted capability behavior and contract | `spec.md` | Yes | Authoritative What |
| Accepted implementation architecture | `design.md` | Yes | Authoritative How |
| Accepted system scenarios, boundaries, invariants, terminology, history | `_context/` | Yes | Authoritative shared context |

Architecture does not automatically belong in `specs/`. A proposed architecture remains in `specs_review/` until the user accepts it.

SDS itself creates no mandatory plan-first or confirmation-first gate. A plan is a useful process artifact for complex work, not an authorization ceremony. Ask for confirmation only when the request leaves intent, authority, or a material product choice unresolved; do not pause routine in-scope implementation merely because SDS is active.

When a proposal is accepted:

1. Keep the original assessment in `specs_review/`.
2. Extract only accepted decisions.
3. Update affected `spec.md`, `design.md`, and `_context/` documents.
4. Remove or deprecate contradictory durable statements.
5. Implement against the promoted durable state.
6. Do not create links from `specs/` to `specs_review/`.

## 3. Scenario and capability coverage

Start with actors and complete journeys. For each affected scenario, define:

- entry conditions and identity;
- happy path and completion state;
- authorization and data-scope boundaries;
- invalid input and dependency failures;
- retry, recovery, and audit behavior;
- observable signals for support and operations;
- PC/H5/mobile differences when the interface is user-facing.

Route ownership before editing. Choose the module from the user scenario, business authority, and lifecycle owner—not from the database table, implementation package, or directory where code happens to exist. Every module that owns capabilities needs `_context/` describing its journeys and boundary. Keep system context concise and put exact behavior in the owning capability spec. If schema evolution, release, migration, or runtime behavior is important but has no owner, create a system/ops capability instead of placing it under a nearby business module or burying it in a general architecture note.

For stateful workflows, make reachability explicit:

- enumerate initial/empty, active, terminal, retry, and recovery states;
- prove the first valid action is possible from an empty system;
- reject circular prerequisites such as requiring a plan before a position can exist while requiring a position before a plan can be created;
- define scheduled completion, missed-run detection, idempotent retry, backfill, and operator-visible reconciliation;
- distinguish internal immutable identifiers from external/business identifiers, including visibility, editability, uniqueness, and creator/owner binding.

For data pipelines, name one runtime source of truth and its writer. Define ingestion/materialization before projections or compatibility exports, and state how derived artifacts are rebuilt and reconciled. A compatibility CSV, cache, or report must not silently become a second writable truth.

Acceptance criteria must be atomic and externally verifiable. Avoid criteria such as “the page is reasonable” or “deployment works.” Define concrete outcomes, for example:

- the mobile edit experience uses a full-page or bottom-sheet flow and does not overflow at the supported viewport;
- a profile update sends the authenticated user's required identifier and returns a deterministic error when absent;
- routine deployment connects as the configured non-root account;
- activation occurs only after the new runtime, migrations, and health checks pass;
- a failed post-activation check restores the previous release and static assets;
- retention keeps the configured number of healthy releases.

## 4. Implementation and test discipline

Use `@sds-trace: <capability_id>:AC-n` at important implementation and test boundaries when traceability is enabled.

Derive tests from the spec rather than reverse-engineering current code. Independent test design means logical separation, not mandatory agent delegation:

- use a separate agent only when user/repository policy permits it;
- otherwise hide implementation details during a dedicated spec-only test-design pass;
- validate happy paths, boundaries, failures, recovery, and side effects;
- for UI, include supported viewport and interaction checks;
- for releases and migrations, include failure-injection or rollback checks where safe.

After implementation, inspect the full change set for stale entrypoints, generated build output mixed into source, duplicated code paths, obsolete docs, untracked files, and unrelated edits.

## 5. Verification layers

Do not collapse all validation into one “SDS passed” statement.

| Layer | Typical checks | What it establishes |
|---|---|---|
| SDS baseline | structure, headings, artifact placement, drift, traces, heuristic side effects | repository/spec discipline |
| Project quality | unit/integration tests, lint, type checks, frontend tests/build, shell syntax | implementation quality |
| Data evolution | migration ordering, upgrade from supported state, idempotence policy, ledger | schema transition safety |
| Release rehearsal | package/build, runtime discovery, permissions, atomic switch, rollback | deployability |
| Environment smoke | health, redirects, assets, auth/config presence, critical journeys | deployed behavior |
| Observation | structured logs, request IDs, error-rate window, disk/release retention | early runtime health |

Declare deterministic project-quality commands in `.sds.harness.yaml` as argument arrays:

```yaml
verification_commands:
  - ["{python}", "-m", "pytest", "tests/"]
  - ["{python}", "-m", "ruff", "check", "app", "tests"]
  - ["npm", "run", "test", "--prefix", "frontend"]
  - ["npm", "run", "build", "--prefix", "frontend"]
```

The harness executes these commands without a shell. `{python}` resolves to the interpreter running the harness, which keeps virtual-environment selection cross-platform. Keep secrets out of command arguments. Environment-specific deployment and production smoke commands should remain in controlled release tooling rather than a generic local harness.

Do not invent a credential or token dependency for release verification. Use an authentication-independent health/readiness endpoint to verify the exact release identity when the service contract supports it. Run authenticated smoke only for journeys whose owning spec requires it and only through an established credential source.

## 6. Operations, migration, and release contracts

### Database evolution

For each schema change, define:

- monotonically ordered migration identity/version;
- supported starting schema state;
- forward operation and transaction boundary;
- backward/forward application compatibility during rollout;
- idempotence or explicit single-run semantics;
- failure handling and recovery/backout strategy;
- migration ledger update and verification query;
- backup or restore requirement for destructive changes.

Do not treat ad-hoc startup DDL as sufficient version management.

### Frontend source and build output

Define:

- source directory and framework entrypoint;
- generated output directory;
- whether generated files are tracked or release-only;
- removal date/path for legacy entrypoints;
- test/build commands and supported PC/H5 viewports;
- serving permissions and asset smoke checks.

Source code should not be maintained directly inside a deployment output directory unless the accepted design explicitly requires it.

### Release lifecycle

Define:

- SSH/deployment identity and privilege boundary;
- environment/configuration file ownership and load path;
- runtime discovery and supported version;
- dependency/virtual-environment creation or reuse policy;
- pre-activation preparation and migration order;
- atomic application and static-asset activation;
- restart permissions and service manager behavior;
- post-activation health and critical-path smoke checks;
- automatic rollback boundaries;
- release pruning policy and minimum rollback inventory;
- file/directory permissions required by the web/service account;
- post-release observation duration and log signals.

Model deployment as a state machine, especially around irreversible boundaries. If a migration makes the previous runtime unable to understand the new schema, keep the previous writer stopped after migration; do not restart it merely to reach activation. Activate and verify the compatible new runtime, and define rollback as application rollback plus database restore/forward recovery when schema compatibility requires it.

Health evidence should identify what is running, not only that a process answered. Define stable fields such as release/build ID, source revision, schema revision, and dependency readiness as appropriate. Keep source synchronization rules (for example fetch/rebase before push) separate from build, deployment, and post-release validation; do not add a remote pre-push gate unless repository policy explicitly requires one.

Secrets belong in the deployment platform or protected shared environment files, never specs, diagnostics, command arguments, or logs. Specs record variable names and ownership boundaries only.

## 7. Harness responsibilities and limits

The bundled `sds_self_check.py` is a standard-library baseline validator. It can:

- check repository structure and required spec headings;
- ensure `specs_review/` is gitignored;
- reject unclassified `_context/` files and durable links to `specs_review/`;
- detect coarse change-set drift between implementation and specs;
- validate referenced capability/AC identifiers;
- heuristically scan selected source types for undeclared domains/tables;
- execute configured verification commands;
- write structured diagnostics.

It cannot, without project-specific extensions:

- prove that changed code maps to the correct spec rather than merely any changed spec;
- prove semantic correctness or exhaustive side-effect safety;
- fuzz contracts automatically;
- validate visual quality or browser interaction automatically;
- establish migration safety across real production states;
- prove remote deployment health.

Treat those as explicit project test/release responsibilities. Do not describe an unconfigured capability as if the baseline harness performs it.

The project-local checker is the repository entrypoint. The skill-owned checker is an upstream reference. Use `--refresh-harness` for managed copies; customized project checkers receive a candidate under `specs_review/` and require manual merging.

## 8. Completion checklist

- [ ] Accepted behavior is represented in `spec.md`.
- [ ] Accepted implementation decisions are represented in `design.md`.
- [ ] Shared scenarios/boundaries are current without process notes.
- [ ] The capability is in the owning module, its ID matches the path, and that module has `_context/`.
- [ ] Stateful workflows are reachable from empty/initial state without circular prerequisites.
- [ ] Runtime truth, writers, projections, retry/backfill, and reconciliation are explicit where data is materialized.
- [ ] Assessments and evidence remain in `specs_review/`.
- [ ] Code, tests, configuration, migrations, build output, and deployment scripts match the durable state.
- [ ] SDS baseline passes.
- [ ] Project verification commands pass.
- [ ] Release-specific smoke and observation checks pass when deployment is in scope.
- [ ] Release evidence identifies the exact running build without inventing undocumented credential gates.
- [ ] Working tree has been reviewed for stale, generated, untracked, or unrelated files.
- [ ] Commit/push/deploy actions have the required user authorization.
