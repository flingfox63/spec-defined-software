# sds-ideator (The Brainstorming Skill)

`sds-ideator` is the **front-door** of the SDS lifecycle. It is designed to engage with developers and product managers to refine abstract goals into actionable, verifiable specifications.

> [!NOTE]
> **Ecosystem Status: 🟡 In Progress / 模块开发状态：进行中**
> This module (`sds-ideator`) is currently **In Progress** as outlined in our [Roadmap](../index.md#ecosystem-roadmap). The specifications and instructions below describe the target design and behavioral interface, but the physical skill package is not yet fully active.
> 本模块目前处于**开发中**阶段。下述规范和指令描述了其目标架构和行为定义，但其实体技能包尚未正式激活。

---

## Key Capabilities

1. **Socratic Interviewing**: Instead of accepting a simple one-sentence instruction (e.g., *"Make a check out button"*), the ideator asks logical clarifying questions about edge cases, constraints, and business rules.
2. **Gherkin-Style Formulation**: Automatically translates refined scenarios into structured `Given-When-Then` Acceptance Criteria (ACs).
3. **Drafting Stage Separation**: Saves all raw research, Q&A records, and comparison drafts in the gitignored `specs_review/` workspace to prevent main branch noise.
4. **Promotion Mapping**: Once approved, compiles the finalized, product-oriented specification and saves it as `spec.md` under `specs/`.

---

## Agent Usage Instructions
When an LLM agent activates the `sds-ideator` skill, it must:
1. Resolve business boundaries from accepted context; ask only when material ambiguity remains.
2. Identify actors, preconditions, happy paths, and error constraints.
3. Establish the schema structures conceptually (no physical datatypes or programming language terms).

For every AC, record the durable scenario source, business inference, ambiguity disposition and positive/counterexample expectations in `ac_derivation`. Promote accepted conclusions without referencing temporary review artifacts.
