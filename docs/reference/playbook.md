# The SDS Team Playbook

This playbook outlines the essential guidelines that every developer, reviewer, and AI agent must adhere to when working with SDS.

---

## 🛡️ Key Rules of Engagement

1. **Specs Over Code**: The spec wins when implementation and accepted intent differ. If the code behavior is correct and newly accepted, **update the specification first**, then modify the code and tests.
2. **Active Path-Aligned IDs**: Verify that every capability lives under the owning module, and its `capability_id` matches that path (e.g. `specs/user_auth/login/` must have ID `user_auth.login`).
3. **No Bloated Global State**: Keep global contexts concise. Put precise and localized behavior in the specific capability's `spec.md` and `design.md`.
4. **No Git-tracked Review Files**: Never check in files located in `specs_review/`. They are temporary and local-only. Keep durable agreements in `specs/`. Durable documents must not depend on review artifacts through any reference notation; promote accepted conclusions instead.
5. **Scenario-grounded ACs**: Every AC needs an `ac_derivation` record with a durable context source, business reasoning, ambiguity disposition and positive/counterexample expectations. Resolve material ambiguity against the actor, initial state and goal; ask the user when context cannot decide.
6. **Business and technical ownership**: `spec.md` describes observable business behavior; `design.md` maps it to mechanisms and tests. Do not infer requirements from existing code.

---

## ⚡ The Standard SDS Verification Checklist

Before pushing a feature or delivering a requirement, complete this quick checklist:

* [ ] **Spec Updated**: Does the spec represent the exact accepted business behavior?
* [ ] **Design Updated**: Does `design.md` map every AC to its technical mechanism, positive test and boundary/counterexample test, with applicable physical contracts and migrations?
* [ ] **Derivations Complete**: Does every AC have a valid context source and resolved reasoning, including failure and recovery cases?
* [ ] **Scenario Review Complete**: Were expectations independently derived from context/spec before reading code, and challenged with counterexamples?
* [ ] **Zero-Drift Validated**: Did you execute `sds check` successfully?
* [ ] **Traceability Annotated**: Did you add `@sds-trace` annotations to all relevant implementation lines and test classes?
* [ ] **Automated Tests Passing**: Have all unit, integration, and contract tests passed?
* [ ] **Review Cleaned**: Did you verify that no temporary artifacts or screenshots have been accidentally added to the git-tracked `specs/` folder?

The enabled derivation gate applies to all AC statuses. Existing projects need
to backfill records; temporarily disabling `enforce_ac_derivation` does not count
as scenario verification. Trace markers and complete records are structural
checks, not proof of correct behavior. See [templates](templates.md).

---

## 🤖 AI Agent Playbook Reference

If you are an **LLM AI Coding Agent** (e.g., Antigravity) working on this repository, you must read and adhere to the specialized, highly-actionable [AI Agent Playbook](https://github.com/flingfox63/spec-defined-software/blob/main/references/sds-playbook.md). It outlines:
- Interactive slash command workflows
- Multi-agent orchestration and role delegation protocols
- Detailed verification-before-completion feedback loops
