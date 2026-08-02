# sds-ideator (The Brainstorming Skill)

`sds-ideator` is the **front-door** of the SDS lifecycle. It is designed to engage with developers and product managers to refine abstract goals into actionable, verifiable specifications.

---

## Key Capabilities

1. **Socratic Interviewing**: Instead of accepting a simple one-sentence instruction (e.g., *"Make a check out button"*), the ideator asks logical clarifying questions about edge cases, constraints, and business rules.
2. **Gherkin-Style Formulation**: Automatically translates refined scenarios into structured `Given-When-Then` Acceptance Criteria (ACs).
3. **Drafting Stage Separation**: Saves all raw research, Q&A records, and comparison drafts in the gitignored `specs_review/` workspace to prevent main branch noise.
4. **Promotion Mapping**: Once approved, compiles the finalized, product-oriented specification and saves it as `spec.md` under `specs/`.

---

## Agent Usage Instructions
When an LLM agent activates the `sds-ideator` skill, it must:
1. Actively grill the user on business boundaries.
2. Identify actors, preconditions, happy paths, and error constraints.
3. Establish the schema structures conceptually (no physical datatypes or programming language terms).
