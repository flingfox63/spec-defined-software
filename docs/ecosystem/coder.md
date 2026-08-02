# sds-coder (The Implementation Skill)

`sds-coder` is the workhorse of the SDS lifecycle. It coordinates and supervises code generation, ensuring that all implementation steps are strictly bound to accepted specifications.

---

## Key Capabilities

1. **Subagent-Driven Development (SDD)**: For complex changesets, the coder skill spawns dedicated, focused subagents to handle isolated files or modules. This maintains tight context boundaries and improves code quality.
2. **Automatic Trace Annotation**: Automatically injects `@sds-trace: <capability_id>:AC-n` tag comments at the entry and exit points of implementation methods and test suites.
3. **Defense-in-Depth Test Generation**: Derives automated unit and integration tests directly from the spec's ACs rather than reverse-engineering the written code.
4. **Single-Writer Enforcement**: Verifies that business domains have strict boundary isolation and that no file writes violate local module constraints.
