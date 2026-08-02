# CLI Installation & Usage

SDS is distributed as a central, modular Python CLI package (`sds-cli`).

---

## 1. Installation

The easiest way to install SDS globally is to use our one-line installers. They will check for Python 3, set up an isolated sandbox environment, and automatically configure your system's `PATH`.

### macOS / Linux (One-Line Bash)
```bash
curl -fsSL https://raw.githubusercontent.com/flingfox63/spec-defined-software/main/install.sh | sh
```

### Windows (One-Line PowerShell)
```powershell
irm https://raw.githubusercontent.com/flingfox63/spec-defined-software/main/install.ps1 | iex
```

### Advanced: Python Package Managers

If you prefer to manage the python packages manually:

* **Using pipx**:
  ```bash
  pipx install git+https://github.com/flingfox63/spec-defined-software.git
  ```
* **Using pip** (inside a virtual environment):
  ```bash
  pip install git+https://github.com/flingfox63/spec-defined-software.git
  ```

---

## 2. Command Reference

### `sds install-agents`

Installs the released SDS Agent Skill into supported AI agents and IDEs. By
default, SDS detects the agents present on the machine or used by the current
project, then adds or updates only their SDS MCP server entries.

```text
sds install-agents [--targets detected|auto|all|TARGET,TARGET,...]
                   [--scope user|project]
                   [--project-dir PATH]
                   [--command PATH]
                   [--no-mcp]
                   [--force]
                   [--dry-run]
```

SDS follows the Agent Skills directory convention: a skill is a directory with
a `SKILL.md` instruction file and its related resources. Targets that discover
`.agents/skills` at the selected scope share one released `sds-core` bundle.
Only clients that require their own discovery directory receive a separate
copy. Lifecycle skills that are still marked in progress or planned are not
installed until they are released and packaged.

Cline uses its supported `.cline/skills` directory. Windsurf, Codex, OpenCode,
Cursor, Gemini, Copilot, Roo, and Kilo share `.agents/skills`; Claude Code and
Antigravity continue to use their documented agent-specific user locations
where required. During an upgrade, SDS removes only unchanged, SDS-managed
copies left in Windsurf's older dedicated Skill directories.

#### Supported targets

| Selector | Agent or IDE |
| :--- | :--- |
| `shared` | Shared Agent Skills location |
| `codex` | Codex |
| `opencode` | OpenCode |
| `claude` | Claude Code |
| `cursor` | Cursor |
| `cline` | Cline |
| `antigravity`, `agy` | Antigravity CLI |
| `gemini` | Gemini CLI |
| `copilot`, `vscode` | GitHub Copilot / Visual Studio Code |
| `windsurf` | Windsurf |
| `roo` | Roo Code |
| `kilo` | Kilo Code |

Use automatic detection (the default), `all`, or a comma-separated list:

```bash
sds install-agents
sds install-agents --targets all
sds install-agents --targets codex,opencode,claude
sds install-agents --targets agy,gemini --dry-run
```

Detection uses independent evidence such as an executable on `PATH`, an
installed application, a matching editor extension, or an agent-specific
project-use marker. Directories previously created by SDS are not evidence, so
the installer does not keep selecting an agent merely because it configured
that agent in the past. The command reports the evidence it found. If it finds
no agent, it installs only the shared Skill and leaves all agent-specific MCP
configuration untouched. `auto` is an alias for `detected`; it must not be
combined with explicit target names.

When the SDS executable moves, the installer updates an existing JSON MCP entry
only if it exactly matches the SDS-only structure created by an earlier SDS
release. Entries with custom commands, arguments, environment variables, or
other behavior are preserved as user-owned unless `--force` is selected.

#### Scope and configuration

* `--scope user` is the default and makes the integration available across the
  current user's projects.
* `--scope project --project-dir PATH` installs into one repository's agent
  configuration. This is useful when the setup should be versioned or shared
  with that project's collaborators.
* `--command PATH` records a specific SDS executable in MCP configuration. An
  absolute path is helpful when an IDE does not inherit your shell `PATH`.
* `--no-mcp` installs the Agent Skill without changing MCP configuration.
* `--force` replaces existing SDS-managed installation content when required.
* `--dry-run` prints the planned operations without writing files.

Installation is idempotent. Every managed Skill marker records the semantic
bundle version and an exact content hash. Matching content remains unchanged;
an older managed bundle is updated in place; and an old marker with current
content is upgraded without recopying the bundle. During an upgrade, an
unchanged SDS-managed copy in a superseded target-specific directory is
removed. An unmanaged or locally modified copy is preserved and reported;
`--force` permits removal of a modified SDS-managed legacy copy. Existing
non-SDS skills, MCP servers, and unrelated settings are preserved. Run `sds
version` to see the CLI, validation harness, and Skill bundle versions as
separate release identities.

An empty or whitespace-only JSON configuration created by an agent is treated
as a new configuration and initialized automatically. Malformed non-empty JSON
is preserved unchanged and reported as an error so the installer does not guess
which existing settings were intended.

#### Optional manual MCP setup and troubleshooting

Automatic MCP configuration is the default, so manual editing is normally not
required. For a client whose MCP format is not writable automatically, or when
diagnosing executable discovery, use the equivalent stdio entry:

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

Restart the client after changing its settings. If `sds` cannot be found, use
the absolute path returned by `which sds` on macOS/Linux or `Get-Command sds`
in PowerShell, or re-run the installer with `--command PATH`. Use
`sds install-agents --targets TARGET --dry-run` to confirm which files and
settings SDS intends to manage.

---

### `sds init`
Scaffolds a new SDS workspace in the current directory.
```bash
sds init
```
This command creates:
* `.sds.harness.yaml`: Your project-level configuration file.
* `specs/`: The root directory for your durable specifications.
* `specs/_context/`: Global business dictionaries and blue-prints.

---

### `sds check`
Runs the baseline validation rules over your workspace.
```bash
sds check
```

---

### `sds install-hook`
Installs the automated git pre-commit hook to prevent changesets from violating spec alignment.
```bash
sds install-hook
```

---

### `sds mcp`
Launches the Model Context Protocol (MCP) server over standard input/output (stdio), providing full specification context to compatible agent environments.
```bash
sds mcp
```
