---
sds_kind: authoritative-context
---

# System Blueprint

SDS is distributed as a Python command-line package. The `agent_integration`
module owns installation of the released SDS Agent Skill and MCP registrations
into supported coding agents and IDEs. It does not own the agents themselves or
their runtime discovery implementations.

The package must treat user-owned agent configuration as authoritative. It may
manage only SDS-marked skill bundles and the `sds` MCP entry, while preserving
all unrelated configuration.

The `specification` module owns durable contract validation and author guidance,
including scenario derivation and the boundary between business and technical documents.
