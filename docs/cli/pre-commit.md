# Git Pre-commit Hook Integration

By setting up a Git pre-commit hook, developers can automatically verify code-to-spec consistency locally before any commit is finalized. This prevents non-compliant or drifting changesets from ever reaching the server.

---

## 1. Setting up pre-commit

If you haven't already, install the `pre-commit` framework in your local machine:
```bash
pip install pre-commit
# Or on Mac
brew install pre-commit
```

Initialize pre-commit in your repository:
```bash
pre-commit install
```

---

## 2. Configuration

Add the following block to your project's `.pre-commit-config.yaml` file to integrate SDS checks:

```yaml
repos:
  - repo: https://github.com/flingfox63/spec-defined-software
    rev: v1.0.0  # Put the latest release tag or commit hash here
    hooks:
      - id: sds-check
        stages: [commit]
```

---

## 3. How it Works
When a developer runs `git commit`:
1. Pre-commit automatically creates a sandbox Python environment.
2. It fetches and caches the `sds-cli` package.
3. It executes `sds check` focusing on the staged files.
4. If a spec file was changed but no corresponding implementation file was modified (or vice versa), the commit is blocked, showing a diagnostic explanation of the drift.
