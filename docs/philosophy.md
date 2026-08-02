# Core Philosophy & System Architecture

At its heart, SDS is built on clean division of business boundaries and technical isolation. This page outlines the three golden rules of SDS modeling.

---

## 1. Module vs. Capability

To avoid fragmentation and spec bloat, SDS separates business domains from individual transactional features:

* **Module (Business Subdomain)**: A high-level, stable noun representing a macro business area (e.g., `order`, `billing`, `user_auth`). Each module contains its own cohesive `_context/` directories (glossaries, domain models, etc.).
* **Capability (User Feature Scenario)**: A specific, actionable business transaction/lifecycle inside a Module (e.g., `place_payment_order`, `refund_payment`).

### ⚠️ The Golden Rule: Capability $\neq$ API Interface

> [!IMPORTANT]
> **A Capability is NOT a physical API interface/endpoint.** 
> A Capability represents business-value scenarios from the user/product perspective (defined in `spec.md`). A single Capability (like `place_payment_order`) can be physically realized by multiple API endpoints (e.g., separate redirect vs direct-debit endpoints) or polymorphic parameter routes, which are mapped solely in `design.md`. 
> 
> 1-to-1 mapping of APIs to Capabilities is a strict anti-pattern that leads to information duplication and spec fragmentation.

---

## 2. Hub-and-Spoke: Team Isolation

When multiple teams and projects inside an organization adopt SDS, copying raw python scripts to every single directory becomes a maintenance nightmare.

Instead, we use the **Hub-and-Spoke Model**:

```text
       [ Central SDS Repo (Hub) ]
         ├── sds-cli (Python Package)
         ├── Standard Templates
         └── pre-commit Hooks
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
[ Project A (Spoke) ]   [ Project B (Spoke) ]
  ├── .sds.harness.yaml   ├── .sds.harness.yaml
  └── specs/              ├── specs/
                          └── src/
```

### Why this Model is Superior:
1. **Zero Harness Bloat**: Spoke repositories do not check in any tooling engine files. Their git trees remain 100% clean and professional.
2. **Version Pinning & Clean Upgrades**: The core is updated centrally. Projects specify their version in standard dev packages (e.g., in `requirements-dev.txt` or `.pre-commit-config.yaml`).
3. **No Drift on the Tooling Itself**: Standard pre-commit hooks verify compliance transparently inside sandboxed virtualenvs.

---

## 3. Separation of Review and Durable Workspace

To avoid cluttering Git with research and temporary files, SDS enforces a strict separation:

* **`specs_review/` (Temporary drafting kitchen)**: Local-only, gitignored directory. This is where you put raw brainstorming, execution plans, technical assessments, diagnostic logs, and verification runtimes.
* **`specs/` (Durable dining room)**: Authoritative, git-tracked directory. Once a design proposal is accepted by the user/team, the final agreed-upon conclusions are promoted into `specs/` as clean `spec.md`, `design.md` and `_context/` files.

```text
[ specs_review/ (Draft Kitchen) ]  ===>  Promote accepted decisions  ===>  [ specs/ (Dining Room) ]
  ├── assessment.md (gitignored)                                             ├── spec.md (Tracked in Git)
  └── plan.md (gitignored)                                                   └── design.md (Tracked in Git)
```
