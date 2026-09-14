---
capability_id: agent_integration.install_agents
status: implemented
version: 1.2.2
ac_derivation:
  AC-1:
    scenario: ../_context/user-journey.md
    reasoning: "One released skill serves all selected hosts that support shared discovery."
    ambiguity: "none"
    validation: "Hosts sharing a location see one current bundle; a host needing a dedicated location does not rely solely on that shared bundle."
  AC-2:
    scenario: ../_context/user-journey.md
    reasoning: "A host without shared discovery needs its supported dedicated location."
    ambiguity: "none"
    validation: "A dedicated host discovers its installed skill; a host supporting shared discovery receives no unnecessary dedicated copy."
  AC-3:
    scenario: ../_context/user-journey.md
    reasoning: "An empty placeholder has no user decisions to preserve; malformed content does."
    ambiguity: "none"
    validation: "Empty files initialize; malformed files remain byte-identical."
  AC-4:
    scenario: ../_context/user-journey.md
    reasoning: "Only unchanged managed duplicates can be retired without losing user work."
    ambiguity: "none"
    validation: "Managed duplicates retire; customized copies remain."
  AC-5:
    scenario: ../_context/user-journey.md
    reasoning: "Conservative detection serves locally used agents; explicit target selection gives the developer control."
    ambiguity: "none"
    validation: "Detected agents receive skills; no evidence falls back to shared; explicit names override detection."
  AC-6:
    scenario: ../_context/user-journey.md
    reasoning: "Visible release identity and exact content distinguish versions from changes."
    ambiguity: "none"
    validation: "Same content stays current; changed content updates."
  AC-7:
    scenario: ../_context/user-journey.md
    reasoning: "An exact historical SDS invocation is managed while extra behavior is user-owned."
    ambiguity: "none"
    validation: "Canonical paths advance; customized commands remain."
  AC-8:
    scenario: ../_context/user-journey.md
    reasoning: "The developer wants the workflow without changing client connections unless requested."
    ambiguity: "none"
    validation: "Default leaves all MCP bytes unchanged; explicit opt-in adds connections."
  AC-9:
    scenario: ../_context/user-journey.md
    reasoning: "A working host requires its own generation's layout and preservation of unrelated settings."
    ambiguity: "none"
    validation: "First-generation and second-generation layouts work; ambiguous mixed layouts fail without writes."
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
coding agents without redundant copies, with an optional, safe SDS MCP connection when requested.

## 2. Acceptance Criteria

- **AC-1**: Given multiple selected agents that discover the cross-agent Skill location at the chosen scope / When integrations are installed / Then one current SDS Skill bundle serves all of those agents.
- **AC-2**: Given a selected agent that does not discover the cross-agent Skill location at the chosen scope / When integrations are installed / Then that agent receives one current SDS Skill bundle in its supported agent-specific location.
- **AC-3**: Given an agent-created MCP configuration file that is empty or contains only whitespace / When the SDS MCP connection is installed / Then the file becomes valid configuration containing the SDS connection; and given malformed non-empty configuration / Then the original content is preserved and the failure is reported.
- **AC-4**: Given an earlier redundant SDS-managed Skill copy after a target moves to shared discovery / When integrations are upgraded / Then an unchanged managed copy is removed, while an unmanaged or locally modified copy is preserved unless force removal is explicitly requested.
- **AC-5**: Given no targets are explicitly selected / When integrations are installed / Then only agents detected from independent local evidence are selected, falling back to the shared Skill if none are found; explicit named targets override detection and explicit all-target selection remains available.
- **AC-6**: Given an SDS-managed Skill bundle / When it is installed, inspected, built, or upgraded / Then its semantic bundle version and exact content identity are available; content identity determines whether files need replacement, the declared release is consistent across package and Skill metadata, and CLI, harness, and Skill versions are reported with distinct labels.
- **AC-7**: Given an existing MCP connection that exactly matches a canonical SDS invocation from an earlier installation / When the configured SDS executable location changes / Then the connection advances to the new command without requiring force; and given a customized or ambiguous connection / Then it remains preserved unless force replacement is explicitly requested.

- **AC-8**: Given a normal installation or upgrade / When the developer has not requested MCP integration / Then agent skills are installed and every MCP configuration remains untouched; when MCP is requested explicitly / Then connections are configured for the selected targets.
- **AC-9**: Given a developer opting into OpenCode MCP integration / When the supported client generation is selected / Then the connection uses that generation's accepted configuration; an unmodified SDS connection from an earlier incompatible layout is migrated safely, while customized or mixed layouts are preserved with an actionable failure.

## 3. Interface / Contract

### A. Business Inputs

- **Installation scope**: Whether the integration is available to the current user or one project.
- **Selected agents**: One or more supported coding agents and IDEs.
- **SDS command**: The executable each MCP client should invoke.
- **Target selection mode**: Automatic detection by default, every supported target, or an explicit target list.
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

## 5. Installation Safety

A preview must report planned changes without changing the developer's files.
MCP integration is opt-in, including during upgrades; existing connections are
not removed or repaired by a skill-only install. OpenCode defaults to the
first supported client generation; the developer can explicitly select the second.
