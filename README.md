# SDS — Spec-Defined Software (Next-Gen Platform)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: >=3.8](https://img.shields.io/badge/Python->=3.8-blue.svg)](https://python.org)
[![Platform: Cross-Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-green.svg)](https://github.com/flingfox63/spec-defined-software)

**Spec-Defined Software (SDS)** is the central operating system for AI-collaborative software delivery. 

In this paradigm, a business requirement's complete behavioral and business identity is codified in standard Specifications (`spec.md`, the "What") and mapped to technical blueprints (`design.md`, the "How"). The physical code, database migrations, unit tests, and release operations are treated as logical derivatives that can be automatically synthesized, verified, and self-healed by advanced AI engines.

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

---

## 🛠️ Command Line Reference

Once installed, the `sds` command suite is available globally:

* **`sds init`**: Scaffolds a new SDS directory workspace in the active folder, adding the `.sds.harness.yaml` configuration and `specs/` blueprint subfolders.
* **`sds check`**: Runs standard compliance and spec-to-code drift checking.
* **`sds mcp`**: Spawns a 100% standard-compliant stdio Model Context Protocol (MCP) JSON-RPC server for IDE-integrated AI assistants.
* **`sds version`**: Prints current CLI engine version.

---

## 🤖 AI Agent Integration (MCP)

To connect your IDE AI assistant (such as VS Code Cline, Cursor, or Claude Desktop) directly to your SDS validator, add this configuration block to your client's settings:

```json
{
  "mcpServers": {
    "sds": {
      "command": "sds",
      "args": ["mcp"],
      "disabled": false
    }
  }
}
```

This gives your AI assistant instant access to high-precision structural JSON checks in the background.

---

## 📖 Static Documentation Portal

We maintain a beautiful responsive documentation portal built with MkDocs Material.

### Local Preview:
```bash
# Install portal builder
pip install mkdocs-material

# Run hot-reloading development server
mkdocs serve
```
Open `http://localhost:8000` in your browser to view the interactive guides, visual workflows, and playbooks.

### CI/CD Auto-Deployment:
Pushing changes to the `main` branch automatically triggers the [.github/workflows/docs.yml](file:///.github/workflows/docs.yml) workflow to publish the site to your GitHub Pages domain.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.
