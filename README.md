# SDS — Spec-Defined Software (Next-Gen Platform)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: >=3.8](https://img.shields.io/badge/Python->=3.8-blue.svg)](https://python.org)
[![Platform: Cross-Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-green.svg)](https://github.com/flingfox63/spec-defined-software)

**Spec-Defined Software (SDS)** is the central operating system for AI-collaborative software delivery. 

In this paradigm, a business requirement's complete behavioral and business identity is codified in standard Specifications (`spec.md`, the "What") and mapped to technical blueprints (`design.md`, the "How"). The physical code, database migrations, unit tests, and release operations are treated as logical derivatives that can be automatically synthesized, verified, and self-healed by advanced AI engines.

### 📐 The Ultimate Vision: Specs as the Future Form of Requirements Delivery

SDS is not just a tool for checking and validating markdown files; **it represents the future form of software requirements delivery.** By organizing the entire specification ecosystem into a cohesive, multi-dimensional web of **"dots, lines, and planes" (有点有线有面)**, SDS establishes a unified, executable cognitive fabric where humans and AI agents can seamlessly co-evolve software:

* **The Plane (面 - System Context)**: Global concepts and context maps (`system-blueprint.md`) outlining the entire business domain universe.
* **The Line (线 - Module Context)**: Module-specific user journeys, domain models, and business flows bridging cohesive end-to-end lifecycles.
* **The Dot (点 - Capability Spec & Design)**: Atomic, transactional scenarios (`spec.md` and `design.md`) modeling specific, verifiable business value-delivery actions.

By locking down **the "WHY" (Purpose & ACs)** conceptually at the product-perspective layer, we establish an unbreakable quality loop (Zero-Drift) enforced statically through `@sds-trace` coverage. Humans focus on steering high-level business motivation and reviewing contracts, while AI agents focus on high-fidelity technical realization, allowing the system to scale and adaptively evolve over time without architectural decay.

---

## 🚀 The Multi-Skill Monorepo Architecture

This repository is designed as a **Monorepo Skill Registry** (Hub-and-Spoke model), cleanly isolating each stage of the software lifecycle into self-contained agentic skills:

```text
spec-defined-software/
├── pyproject.toml              # Global python package build metadata
├── mkdocs.yml                  # Documentation portal mapping
├── install.sh / install.ps1    # Cross-platform one-click global installers
├── docs/                       # High-fidelity static documentation files
└── skills/                     # THE SKILL REGISTRY (Perfect Isolation)
    ├── sds-core/               # 📦 The Core Spec & Trace Linter Engine
    │   ├── SKILL.md            # Agent instructions for verification
    │   ├── templates/          # Blueprints (spec.template, design.template)
    │   ├── tests/              # Core linter regression test suites
    │   └── src/sds/            # Linter & MCP server source code
    ├── sds-ideator/            # 💡 Socratic requirement alignment skill
    ├── sds-architect/          # 📐 Tech design contract synthesizer skill
    ├── sds-coder/              # 💻 Subagent-driven code generator skill
    ├── sds-qa/                 # 🧪 AC-driven test synthesis & gatekeeping skill
    └── sds-ops/                # 🚀 Symlink-based atomic deploy/rollback skill
```

---

## 🗺️ SDS Ecosystem Roadmap

The SDS platform is evolving from a baseline linting tool into a fully automated, E2E AI-collaborative software delivery operating system. Below is our development timeline and milestones:

| Milestone / Module | Target | Status | Core Deliverables & Capabilities |
| :--- | :--- | :--- | :--- |
| **`sds-core`**<br>*(The Guardrail)* | Shipped | **🟢 Released** | • Statically verifies directory layouts and Frontmatter states.<br>• Integrates pre-commit Git hooks and global installers.<br>• Exposes standard stdio Model Context Protocol (MCP) server. |
| **`sds-ideator`**<br>*(Socratic PM)* | Q3 2026 | **🟡 In Progress** | • Socratic alignment prompt suites to refine loose ideas into BDD Gherkin ACs.<br>• Synthesizes and drafts initial `spec.md` files in `specs_review/`. |
| **`sds-architect`**<br>*(Lead Engineer)* | Q3 2026 | **🟡 In Progress** | • Compiles accepted product specs into concrete technical schemas.<br>• Auto-generates TypeScript/Go API contracts, database migrations, and `design.md`. |
| **`sds-coder`**<br>*(Autonomous Synthesizer)* | Q4 2026 | **🔵 Planned** | • Subagent-driven code writer implementing functions directly from specs.<br>• Automatically inserts `@sds-trace` anchors and self-heals compiler/drift errors. |
| **`sds-qa`**<br>*(BDD Test Compiler)* | Q4 2026 | **🔵 Planned** | • Synthesizes runnable integration, unit, and E2E test scripts from ACs.<br>• Mandates a quality gate verification prior to deployment triggering. |
| **`sds-ops`**<br>*(Atomic Release)* | Q1 2027 | **🔵 Planned** | • Capistrano-style atomic releases with symbolic-link switching.<br>• Automated virtualenv isolation and remote passwordless rollback controls. |

---

## 📥 One-Click Installation

The easiest way to install the SDS CLI globally with automated `PATH` configuration and dependency isolation:

### macOS / Linux (Bash)
```bash
curl -fsSL https://raw.githubusercontent.com/flingfox63/spec-defined-software/main/install.sh | sh
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/flingfox63/spec-defined-software/main/install.ps1 | iex
```

The one-click installer also installs the released SDS Agent Skill for supported
agents and IDEs, and configures MCP where the client has a writable config
format. You can rerun that step independently with:

```bash
sds install-agents
```

The default is `--targets detected --scope user`: SDS looks for installed agent
commands, applications, extensions, and project-use markers, then configures
only the agents it can identify. If no agent is detected, it installs only the
shared Agent Skill and does not create agent-specific MCP settings. Use
`--targets all` for every supported integration. Agents that discover
`.agents/skills` share one SDS bundle; agent-specific copies are created only
where the selected scope requires them. Use `--scope project --project-dir
PATH` when the integration should belong to one repository instead. Cline uses
`.cline/skills`; Windsurf uses the shared `.agents/skills` bundle. Canonical
SDS-only MCP entries follow an upgraded executable path automatically, while
customized entries remain preserved.

---

## 🛠️ Command Line Reference

Once installed, the `sds` command suite is available globally:

* **`sds init`**: Scaffolds a new SDS directory workspace in the active folder, adding the `.sds.harness.yaml` configuration and `specs/` blueprint subfolders.
* **`sds check`**: Runs standard compliance and spec-to-code drift checking.
* **`sds install-agents`**: Detects installed agents, installs the released SDS Agent Skill, and configures the matching SDS MCP entries.
* **`sds mcp`**: Spawns a 100% standard-compliant stdio Model Context Protocol (MCP) JSON-RPC server for IDE-integrated AI assistants.
* **`sds version`**: Prints the CLI, harness, and released Skill bundle versions separately.

---

## 🤖 AI Agent Integration (Agent Skills + MCP)

SDS uses the open Agent Skills directory convention and supports user- or
project-scoped installation for:

`shared`, `codex`, `opencode`, `claude`, `cursor`, `cline`, `antigravity` (`agy`),
`gemini`, `copilot` (`vscode`), `windsurf`, `roo`, and `kilo`.

Auto-detect installed agents, select every supported target explicitly, or
choose a comma-separated subset:

```bash
sds install-agents
sds install-agents --targets all
sds install-agents --targets codex,claude,agy
sds install-agents --targets cursor --scope project --project-dir /path/to/repo
```

The operation is idempotent. Each managed Skill records a semantic bundle
version and exact content hash. Re-running it keeps matching content unchanged,
updates an older managed bundle in place, and refreshes legacy markers without
duplicating Skill content. Earlier unmodified SDS-managed copies in superseded
agent-specific directories are removed; user-owned or locally modified copies
are preserved. Unrelated skills, servers, and settings are also preserved. It
installs only released skills currently included in the package; roadmap skills
such as `sds-ideator` and `sds-coder` are not presented as available before they
ship.

Useful options include `--command PATH` to record a specific SDS executable,
`--no-mcp` to install only the Agent Skill, `--force` to replace SDS-managed
content, and `--dry-run` to preview changes.

Manual MCP setup is therefore optional. If automatic configuration is not
supported by a particular client, or you are troubleshooting executable
discovery, add the following entry to that client's MCP settings and restart
the client:

```json
{
  "mcpServers": {
    "sds": {
      "command": "sds",
      "args": ["mcp"]
    }
  }
}
```

If the client cannot find `sds`, replace `"command": "sds"` with the absolute
path reported by `which sds` (macOS/Linux) or `Get-Command sds` (PowerShell), or
re-run `sds install-agents --command /absolute/path/to/sds`.

---

## 📖 Static Documentation Portal

We maintain a beautiful responsive documentation portal built with MkDocs Material.

### Local Preview:
```bash
# Install portal builder
pip install mkdocs-material mkdocs-static-i18n

# Run hot-reloading development server
mkdocs serve
```
Open `http://localhost:8000` in your browser to view the interactive guides, visual workflows, and playbooks.

### CI/CD Auto-Deployment:
Pushing changes to the `main` branch automatically triggers the [.github/workflows/docs.yml](file:///.github/workflows/docs.yml) workflow to publish the site to your GitHub Pages domain.

## 💖 Heritage & Inspiration

Spec-Defined Software (SDS) is heavily inspired by and evolved from GitHub's pioneering [spec-kit](https://github.com/github/spec-kit) methodology. 

We extend the original `spec-kit` patterns by introducing automated zero-drift linting checks, multi-agent AI orchestration guards, and physical bidirectional traceability (`@sds-trace`) engineered specifically for the AI native era.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.
