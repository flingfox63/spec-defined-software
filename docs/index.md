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

To move away from passive "linting" and support the entire software delivery pipeline, SDS orchestrates multiple specialized agent skills:

1. **`sds-ideator` (Demand Phase)**: A Socratic Brainstorming Skill that guides developers in refining fuzzy user requirements into crisp, Gherkin-style Acceptance Criteria.
2. **`sds-architect` (Design Phase)**: Translates product spec requirements into formal API contracts, DB schema migrations, and technical patterns.
3. **`sds-coder` (Implementation Phase)**: Spawns isolated coding subagents to implement physical features and unit tests, automatically maintaining `@sds-trace` coverage.
4. **`sds-qa` (Verification Phase)**: **🧪 The Quality Gatekeeper.** Automatically synthesizes test suites from `spec.md` ACs and connects them back to `user-journey.md` (User Story) flows to achieve complete requirement closure.
5. **`sds-ops` (Delivery Phase)**: Executes atomic deployments using symlinked environments, manages database migration ledgers, and runs regression smoke checks.

---

## 📦 Instant Quickstart

Get started with the SDS CLI in seconds:

### 1. Installation
Install the CLI tool globally using our one-line installer:
```bash
curl -fsSL https://raw.githubusercontent.com/flingfox63/spec-defined-software/main/install.sh | sh
```

### 2. Initialization
Run the initialization scaffold in the root of your project directory:
```bash
sds init
```
This generates the `.sds.harness.yaml` config and sets up the standard `specs/` directory layout.

### 3. Run Verification Checks
Verify your repository structure, code annotations, and check for spec-to-code drift:
```bash
sds check
```

---

> [!NOTE]
> SDS is fully compatible with modern Multi-Agent orchestration frameworks and MCP protocols, giving your AI coding assistant native tools to read, update, and test specs.
