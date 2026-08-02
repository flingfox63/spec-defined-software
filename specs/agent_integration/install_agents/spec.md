---
capability_id: agent_integration.install_agents
status: implemented
version: 1.2.1
side_effects:
  database: []
  external_apis: []
  file_system:
    - "Selected agent skill directories"
    - "Selected agent MCP configuration files"
---

# Capability Specification: Install Agent Integrations

## 1. Purpose

Let a developer install or upgrade one released SDS Agent Skill across selected
coding agents without redundant copies, while safely configuring each agent's
SDS MCP connection.

## 2. Acceptance Criteria

- **AC-1**: Given multiple selected agents that discover the cross-agent Skill location at the chosen scope / When integrations are installed / Then one current SDS Skill bundle serves all of those agents.
- **AC-2**: Given a selected agent that does not discover the cross-agent Skill location at the chosen scope / When integrations are installed / Then that agent receives one current SDS Skill bundle in its supported agent-specific location.
- **AC-3**: Given an agent-created MCP configuration file that is empty or contains only whitespace / When the SDS MCP connection is installed / Then the file becomes valid configuration containing the SDS connection; and given malformed non-empty configuration / Then the original content is preserved and the failure is reported.
- **AC-4**: Given an earlier redundant SDS-managed Skill copy after a target moves to shared discovery / When integrations are upgraded / Then an unchanged managed copy is removed, while an unmanaged or locally modified copy is preserved unless force removal is explicitly requested.
- **AC-5**: Given no agent targets are explicitly selected / When integrations are installed / Then SDS configures only agents detected from executable, application, extension, or project-use evidence; and when no specific agent is detected / Then SDS installs only the shared Skill without creating agent-specific MCP configuration; while an explicit all-target selection continues to configure every supported target.
- **AC-6**: Given an SDS-managed Skill bundle / When it is installed, inspected, built, or upgraded / Then its semantic bundle version and exact content identity are available; content identity determines whether files need replacement, the declared release is consistent across package and Skill metadata, and CLI, harness, and Skill versions are reported with distinct labels.
- **AC-7**: Given an existing MCP connection that exactly matches a canonical SDS invocation from an earlier installation / When the configured SDS executable location changes / Then the connection advances to the new command without requiring force; and given a customized or ambiguous connection / Then it remains preserved unless force replacement is explicitly requested.

## 3. Interface / Contract

### A. Business Inputs

- **Installation scope**: Whether the integration is available to the current user or one project.
- **Selected agents**: One or more supported coding agents and IDEs.
- **SDS command**: The executable each MCP client should invoke.
- **Target selection mode**: Automatic detection, every supported target, or an explicit target list.
- **Safety options**: Whether MCP configuration is enabled, whether changes are previewed, and whether managed conflicts may be forced.

### B. Business Outputs

- **Integration events**: Per-target outcomes describing installed, current, planned, preserved, removed, or failed work.
- **Completion status**: Success only when no integration event failed.
- **Bundle identity**: Human-readable Skill version plus an exact content fingerprint.
- **Connection ownership outcome**: Whether an MCP entry was installed, advanced, already current, preserved as user-owned, or failed.

## 4. Business Rules & Edge Cases

- Shared Skill discovery affects Skill placement only; MCP registrations remain agent-specific.
- A shared Skill location is used only when the selected agent supports it at the selected installation scope.
- Automatic detection must not treat files created solely by SDS as proof that an agent is installed.
- Automatic detection is best-effort and never prevents explicit target selection.
- Repeated installation is idempotent.
- Unrelated skills, MCP servers, and settings are preserved.
- A non-empty malformed configuration is not repaired automatically because its intended content cannot be inferred safely.
- Cleanup applies only to bundles bearing a valid SDS management marker.
- Semantic version is informational; exact bundle content remains the update authority.
- Canonical SDS-only MCP entries are upgrade-compatible; unexpected commands,
  arguments, or additional behavior make an entry user-owned.

## 5. Operational Contract

The installer must work with the Python standard library, write replacement
configuration atomically, and expose a dry-run preview without filesystem
changes.
