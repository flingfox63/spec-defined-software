# SDS Ecosystem Overview

SDS is designed to span the entire software lifecycle. By combining distinct, focused, and cooperative AI agent skills, we transform requirement delivery from a manual coding task into a precise, spec-driven engineering pipeline.

---

## The Cohesive Skill Suite

Explore the separate stages of our delivery lifecycle:

### 1. [sds-ideator](ideator.md) — Requirement Exploration
* Translates fuzzy human requests into Gherkin Acceptance Criteria.
* Eliminates ambiguous product requirements early.

### 2. [sds-architect](architect.md) — Contract & Technical Design
* Bridges the product spec into actual software blueprints.
* Automatically designs API payloads, database migration paths, and schema changes.

### 3. [sds-coder](coder.md) — Subagent-Driven Implementation
* Spawns specialized coding agents to implement code and tests.
* Automatically writes robust `@sds-trace` link annotations.

### 4. [sds-ops](ops.md) — Atomic Release & Rollback
* Automates Capistrano-style atomic container/host deployments.
* Executes database migration steps and rolls back instantly on validation failure.
