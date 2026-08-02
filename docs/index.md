# SDS — Spec-Defined Software (Requirement Delivery Version)

Welcome to the future of software engineering.

**Spec-Defined Software (SDS)** is the transition of requirement delivery from manual coding to precise, AI-collaborative **specification-defining**. In this paradigm, a business requirement's complete behavioral and business identity is codified in its `spec.md` (the "What") and mapped to its technical realization in `design.md` (the "How").

The physical code, database migrations, tests, and deployment configurations are treated as logical derivatives that can be automatically synthesized, verified, and self-healed by advanced AI engines.

---

## 🚀 The SDS Philosophy: Code is Compile Target

Always treat the **Specification** as the absolute source of truth for the entire requirement delivery process. Prioritize the completeness and clarity of the Specification over immediate coding.

```text
  [ User Scenario ] ➔ [ Accepted Spec & Design ] ➔ [ Implementation ] ➔ [ Verification ] ➔ [ Requirement Delivery ]
```

The code is merely a compiled artifact of the delivered requirement. By keeping our edits highly focused on the Spec-first delivery model, we map every change back to an Acceptance Criterion (AC) in the Spec, achieving zero-drift development.

---

## 🛠️ The SDS Core-Centric Lifecycle Suite

Today, the released `sds-core` skill provides specification validation,
traceability checks, Git hooks, and MCP access. The specialized lifecycle skills
below describe the product roadmap; their status in the roadmap table is the
source of truth for availability:

1. **`sds-ideator` (Demand Phase, in progress)**: Planned Socratic workflows for refining fuzzy requirements into Gherkin-style Acceptance Criteria.
2. **`sds-architect` (Design Phase, in progress)**: Planned translation of accepted product specs into technical contracts and `design.md`.
3. **`sds-coder` (Implementation Phase, planned)**: Planned implementation assistance with `@sds-trace` coverage.
4. **`sds-qa` (Verification Phase, planned)**: Planned AC-driven test synthesis and quality gates.
5. **`sds-ops` (Delivery Phase, planned)**: Planned atomic deployment and rollback workflows.

---

## 📦 Instant Quickstart

Get started with the SDS CLI in seconds:

### 1. Installation
Install the CLI tool globally using our one-line installer:
```bash
curl -fsSL https://raw.githubusercontent.com/flingfox63/spec-defined-software/main/install.sh | sh
```

### 2. Install into AI agents and IDEs

Auto-detect installed agents, install the released SDS Agent Skill, and
configure MCP:

```bash
sds install-agents
```

The default is user-scoped and detects agents from their commands,
applications, extensions, or project-use markers. With no match, SDS installs
only the shared Skill and does not create agent-specific MCP settings. You can
select all targets, choose a subset, or keep the integration in one repository:

```bash
sds install-agents --targets all
sds install-agents --targets codex,opencode,claude,agy
sds install-agents --targets cursor --scope project --project-dir /path/to/repo
```

Supported selectors are `shared`, `codex`, `opencode`, `claude`, `cursor`, `cline`,
`antigravity` (`agy`), `gemini`, `copilot` (`vscode`), `windsurf`, `roo`, and
`kilo`. SDS follows the Agent Skills directory convention. Installation is
idempotent: agents that support `.agents/skills` share one SDS bundle, while
agent-specific copies are used only where required. Managed markers record the
Skill bundle version and content hash, so older bundles update in place without
creating duplicates. Existing non-SDS skills, MCP servers, and settings are
preserved. Use `--no-mcp` for skill-only installation or `--dry-run` to preview
changes. `sds version` reports the CLI, harness, and Skill bundle versions
separately.

### 3. Initialization
Run the initialization scaffold in the root of your project directory:
```bash
sds init
```
This generates the `.sds.harness.yaml` config and sets up the standard `specs/` directory layout.

### 4. Run Verification Checks
Verify your repository structure, code annotations, and check for spec-to-code drift:
```bash
sds check
```

### Optional manual MCP troubleshooting

Automatic MCP configuration is enabled by default. If a client cannot find the
CLI, re-run `sds install-agents --command /absolute/path/to/sds`; use
`--no-mcp` if you prefer to manage MCP yourself. A manual stdio entry uses
`sds` as the command and `["mcp"]` as its arguments.

## 🗺️ Ecosystem Roadmap

The SDS platform is evolving from a baseline linting tool into a fully automated, E2E AI-collaborative software delivery operating system. Below is our development timeline and milestones:

| Milestone / Module | Target | Status | Core Deliverables & Capabilities |
| :--- | :--- | :--- | :--- |
| **`sds-core`**<br>*(The Guardrail)* | Shipped | **🟢 Released** | • Statically verifies directory layouts and Frontmatter states.<br>• Integrates pre-commit Git hooks and global installers.<br>• Exposes standard stdio Model Context Protocol (MCP) server. |
| **`sds-ideator`**<br>*(Socratic PM)* | Q3 2026 | **🟡 In Progress** | • Socratic alignment prompt suites to refine loose ideas into BDD Gherkin ACs.<br>• Synthesizes and drafts initial `spec.md` files in `specs_review/`. |
| **`sds-architect`**<br>*(Lead Engineer)* | Q3 2026 | **🟡 In Progress** | • Compiles accepted product specs into concrete technical schemas.<br>• Auto-generates TypeScript/Go API contracts, database migrations, and `design.md`. |
| **`sds-coder`**<br>*(Autonomous Synthesizer)* | Q4 2026 | **🔵 Planned** | • Subagent-driven code writer implementing functions directly from specs.<br>• Automatically inserts `@sds-trace` anchors and self-heals compiler/drift errors. |
| **`sds-qa`**<br>*(BDD Test Compiler)* | Q4 2026 | **🔵 Planned** | • Synthesizes runnable integration, unit, and E2E test scripts from ACs.<br>• Mandates a quality gate verification prior to deployment triggering. |
| **`sds-ops`**<br>*(Atomic Release)* | Q1 2027 | **🔵 Planned** | • Capistrano-style atomic releases with symbolic-link switching.<br>• Automated virtualenv isolation and remote passwordless rollback controls. |

## 💖 Heritage & Inspiration

Spec-Defined Software (SDS) is proud of its roots and is heavily inspired by and evolved from GitHub's [spec-kit](https://github.com/github/spec-kit) methodology. We extend the original `spec-kit` patterns by introducing automated zero-drift linting, multi-agent LLM orchestration safety gates, and physical bidirectional traceability (`@sds-trace`) engineered specifically for the AI native era.

---

> [!NOTE]
> The released `sds-core` skill integrates with the supported Agent Skills and
> MCP environments listed above. Lifecycle skills marked in progress or planned
> are not installed until they ship.
