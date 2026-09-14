---
sds_kind: authoritative-context
---

# Agent Integration User Journey

A developer installs or upgrades SDS and expects locally used agents to be
selected by default through conservative detection. Explicit target lists let
the developer choose which agents to install or upgrade; all-target mode remains
available. With no evidence, only the shared Skill is installed. MCP changes
require an explicit request, including repairs to earlier SDS configurations.
Normal installation neither probes nor repairs MCP files. Shared discovery
avoids redundant copies; compatible agents can discover the same bundle.

Agent-specific locations remain necessary when a client does not discover the
cross-agent directory at the selected scope. Existing user-owned skills and
configuration are never silently replaced or removed. Operators can distinguish
the CLI package, validation harness, and installed Skill bundle versions while
exact content identity controls file replacement.

When an SDS upgrade changes the executable location, an existing connection
that still matches the canonical SDS invocation advances to the new command.
Customized or ambiguous connections remain user-owned and are preserved for
manual review.

When opting into MCP, an OpenCode developer expects the client to remain
launchable. First-generation clients need a different connection layout from
second-generation clients. SDS defaults to the first generation and supports
an explicit second-generation choice. Only recognizable SDS-only legacy
entries can move automatically; mixed or customized layouts require manual
resolution and must not be partially rewritten.
