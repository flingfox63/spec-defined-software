# sds-qa (Quality Assurance & Test Synthesis Skill)

This directory is an architectural placeholder for the **`sds-qa`** agentic skill.

## 🎯 The Mission
The `sds-qa` skill bridges the gap between implementation (`sds-coder`) and production release (`sds-ops`). It focuses on **Acceptance-Criteria-Driven Test Synthesis and Execution Gatekeeping**.

## 🚀 Future Scope
* **Test Synthesis**: Automatically translate AC (Acceptance Criteria) declared in `spec.md` into functional, end-to-end, and unit test suites matching the project's tech stack (e.g., PyTest, Jest, Playwright).
* **Regression Runner**: Orchestrate local and containerized test executions.
* **Release Gatekeeper**: Lock the deployment pipeline (`sds-ops`) until verification coverage is 100% and zero-drift is certified by `sds-core`.
