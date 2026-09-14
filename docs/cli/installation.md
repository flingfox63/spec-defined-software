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
default, SDS detects local agents and installs their Skills without changing
MCP configuration. With no evidence, only the shared Skill is installed. Add
`--with-mcp` to explicitly add or update SDS MCP connections.

```text
sds install-agents [--targets detected|auto|all|TARGET,TARGET,...]
                   [--scope user|project]
                   [--project-dir PATH]
                   [--command PATH]
                   [--with-mcp | --no-mcp]
                   [--opencode-config-version v1|v2]
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

Detection is the default. Use a comma-separated target list to choose which agents to install or upgrade, or `all` for every target:

```bash
sds install-agents
sds install-agents --targets detected
sds install-agents --targets all
sds install-agents --targets codex,opencode,claude
sds install-agents --targets agy,gemini --dry-run
```

Default `--targets detected` selection uses independent evidence such as an executable on `PATH`, an
installed application, a matching editor extension, or an agent-specific
project-use marker. Directories previously created by SDS are not evidence, so
the installer does not keep selecting an agent merely because it configured
that agent in the past. The command reports the evidence it found. If it finds
no agent, it installs only the shared Skill and leaves all agent-specific MCP
configuration untouched. `auto` is an alias for `detected`; it must not be
combined with explicit target names.

When MCP is requested and the SDS executable moves, the installer updates an existing JSON MCP entry
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
* `--with-mcp` opts into MCP configuration. Without it, installation and upgrades
  leave all MCP files untouched. `--no-mcp` remains a compatibility alias for
  the default, and cannot be combined with `--with-mcp`.
* `--opencode-config-version v1|v2` selects the OpenCode layout (default: `v1`).
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

MCP is optional. Enable it with `sds install-agents --with-mcp --targets TARGET`. For a client whose MCP format is not writable automatically, or when
diagnosing executable discovery, for clients using `mcpServers`, use this stdio entry (OpenCode uses the generation-specific layout below):

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
in PowerShell, or re-run the installer with `--with-mcp --command PATH`. Use
`sds install-agents --with-mcp --targets TARGET --dry-run` to confirm which files and
settings SDS intends to manage.

#### OpenCode recovery and client generations

OpenCode v1 expects `mcp.sds`; v2 expects `mcp.servers.sds`. SDS defaults to
v1, matching first-generation clients such as 1.3.17. Check your client with
`opencode --version` and use the matching option:

```bash
# Preview and repair the canonical nested SDS entry emitted by older installers
sds install-agents --targets opencode --with-mcp --dry-run
sds install-agents --targets opencode --with-mcp

# For OpenCode v2 clients only
sds install-agents --targets opencode --with-mcp --opencode-config-version v2
```

A recognized SDS-only legacy entry moves to the selected layout. Other server
settings are retained. Customized legacy entries, duplicate SDS entries, or
mixed layouts with non-SDS servers produce an error without changing the file;
review those settings manually. `--force` does not bypass an ambiguous layout.
A normal skill-only upgrade deliberately leaves existing MCP configuration
untouched, including the earlier incompatible layout.

For project configuration, add `--scope project --project-dir PATH`.
See the official [v1 MCP documentation](https://opencode.ai/docs/fr/mcp-servers/)
and [v2 MCP documentation](https://opencode.ai/v2/docs/mcp-servers).

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
Runs baseline validation rules over your workspace, followed by the project
verification commands declared in `.sds.harness.yaml` when baseline checks pass.

When `enforce_ac_derivation: true` (explicit in new projects), every AC must have an `ac_derivation` record containing `scenario`,
`reasoning`, `ambiguity`, and `validation`. The scenario must reference an existing
durable `_context/` Markdown document, optionally with a valid heading anchor.
Missing records, explicit unresolved markers, placeholders and invalid sources
produce `INVALID_AC_DERIVATION`. Durable references to temporary review artifacts
produce `DURABLE_DOC_LINKS_EPHEMERAL_ARTIFACT` across supported reference notations.

Existing projects without this key retain previous checks and receive one migration warning per run. Backfill all ACs, including draft criteria, then set `enforce_ac_derivation: true`. `refresh-harness` does not silently enable this policy.
For a staged migration, `enforce_ac_derivation: false` explicitly skips this gate
and emits one warning per run; it is not evidence of scenario verification. Complete records
do not prove semantic correctness: independently review every interpretation and
counterexample against context. See [templates](../reference/templates.md).
```bash
sds check
```

---

### `sds install-hook`
Installs the legacy Git hook that invokes a project-local `sds_self_check.py`. It replaces the existing hook. For current CLI-only projects, integrate `sds check` into the existing workflow instead; see [hook integration and limitations](pre-commit.md).
```bash
sds install-hook
```

---

### `sds mcp`
Launches the Model Context Protocol (MCP) server over standard input/output (stdio), providing full specification context to compatible agent environments.
```bash
sds mcp
```

New initialization includes a complete illustrative cancellation scenario at
capability version 1.0.0. `sds init` followed by `sds check` passes baseline checks;
the example remains defined, not implemented. Replace it with accepted project
requirements before writing implementation. Normal install/upgrade does not
probe or repair MCP files. If OpenCode cannot start because of an older broken
entry, manually remove that entry from its config; any subsequent SDS MCP setup
is an explicit `--with-mcp` operation.
