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
