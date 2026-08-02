# The SDS Team Playbook

This playbook outlines the essential guidelines that every developer, reviewer, and AI agent must adhere to when working with SDS.

---

## 🛡️ Key Rules of Engagement

1. **Specs Over Code**: The spec wins when implementation and accepted intent differ. If the code behavior is correct and newly accepted, **update the specification first**, then modify the code and tests.
2. **Active Path-Aligned IDs**: Verify that every capability lives under the owning module, and its `capability_id` matches that path (e.g. `specs/user_auth/login/` must have ID `user_auth.login`).
3. **No Bloated Global State**: Keep global contexts concise. Put precise and localized behavior in the specific capability's `spec.md` and `design.md`.
4. **No Git-tracked Review Files**: Never check in files located in `specs_review/`. They are temporary and local-only. Keep durable agreements in `specs/`.

---

## ⚡ The Standard SDS Verification Checklist

Before pushing a feature or delivering a requirement, complete this quick checklist:

* [ ] **Spec Updated**: Does the spec represent the exact accepted business behavior?
* [ ] **Design Updated**: Does `design.md` outline the exact physical API contracts and DB migrations?
* [ ] **Zero-Drift Validated**: Did you execute `sds check` successfully?
* [ ] **Traceability Annotated**: Did you add `@sds-trace` annotations to all relevant implementation lines and test classes?
* [ ] **Automated Tests Passing**: Have all unit, integration, and contract tests passed?
* [ ] **Review Cleaned**: Did you verify that no temporary artifacts or screenshots have been accidentally added to the git-tracked `specs/` folder?
