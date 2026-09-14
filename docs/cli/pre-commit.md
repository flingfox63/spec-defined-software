# Git Pre-commit Integration

Run the installed `sds check` command in your existing commit workflow to apply
the same baseline and project verification gates used for requirement delivery.
The Git process must be able to find the installed SDS executable.

## Existing hook or commit workflow

Preserve the repository's existing hook and integrate this command with its
failure handling:

```sh
sds check || exit 1
```

SDS currently does not publish a `.pre-commit-hooks.yaml` manifest in this
repository. Do not configure a remote `sds-check` hook ID against this repository.
Use the installed CLI in your existing workflow instead.

## Legacy hook installer

`sds install-hook` currently writes a hook that invokes a project-local
`python sds_self_check.py`, and overwrites the existing hook file. It is intended
for legacy projects containing that checker. New projects initialized by
`sds init` do not receive a local checker; use the CLI integration above.

## What is checked

The checker inspects the workspace, not only staged files. It flags guarded
implementation changes without a spec change in the change set; it does not
require code changes for every documentation edit or prove the correct spec was
changed.

It also validates trace identifiers, requires derivation records for every AC
by default, rejects durable dependencies on temporary review artifacts, and runs
configured project verification after baseline checks pass. Existing projects
must backfill derivation records as described in the
[upgrade guidance](installation.md#sds-check).

A passing hook does not prove semantic correctness or prevent bypassing local
hooks. Independently review every AC against its source scenario and apply the
repository's normal CI and release rules.
