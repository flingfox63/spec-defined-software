---
sds_kind: authoritative-context
---

# Agent Integration User Journey

A developer installs or upgrades SDS once, then expects locally used coding
agents to discover the same released SDS Skill and invoke the same SDS MCP
server without naming every host. Shared discovery locations are preferred so
upgrades do not create independent copies that can drift. Explicit target and
all-target modes remain available when automatic detection is insufficient.

Agent-specific locations remain necessary when a client does not discover the
cross-agent directory at the selected scope. Existing user-owned skills and
configuration are never silently replaced or removed. Operators can distinguish
the CLI package, validation harness, and installed Skill bundle versions while
exact content identity controls file replacement.

When an SDS upgrade changes the executable location, an existing connection
that still matches the canonical SDS invocation advances to the new command.
Customized or ambiguous connections remain user-owned and are preserved for
manual review.
