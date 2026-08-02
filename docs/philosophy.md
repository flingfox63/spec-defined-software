# Core Philosophy & System Architecture

At its heart, **Spec-Defined Software (SDS)** is not merely a tool for linting markdown files or verifying tests; it is the ultimate realization of software engineering where **the specification is the software**. 

SDS is designed to organize the entire software ecosystem as the **future form of requirements delivery**. By constructing a structured, multi-dimensional specification system based on the user's perspective, we establish a cohesive fabric of **"dots, lines, and planes" (有点有线有面)**. This common cognitive map allows both humans and AI agents to continuously, seamlessly, and adaptively co-evolve the system over time.

---

## 🌟 The Three Pillars of Spec-Defined Engineering

The ultimate goal of SDS is to move beyond text-based documentation and establish a living, spec-defined architecture. This is governed by three core pillars:

### 1. Defining the "WHY" (The Goal is Sovereign)
A common pitfall in software engineering is letting physical implementation choices or feature wish-lists dictate software boundaries. Simply asking users what features they want leads to bloated, fragmented software. As Steve Jobs famously remarked, *"People don't know what they want until you show it to them."*

SDS addresses this directly:
* **The specification (`spec.md`) is designed to capture the "WHY" from the user's perspective.** Instead of specifying exact physical screens, button colors, or camelCase API schemas, SDS focuses on the underlying business motivations, the core user goals, and the conceptual boundaries.
* Rather than writing down "what physical software features to build," we lock down the **Purpose** (Why does this capability exist from the user's perspective?) and **Acceptance Criteria** (How do we conceptually verify that the user's motivation has been satisfied?).
* By specifying the "WHY" conceptually, we give implementation agents the maximum technical freedom to synthesize the optimal "HOW" while maintaining a 100% pure business contract.

### 2. Conceptual Decoupling (Decoupling "What" from "How")
To prevent physical details from corrupting business specifications, SDS enforces a strict boundary between conceptual modeling and technical implementation:
* **The Spec (`spec.md`)** defines the conceptual boundaries: *What* is the purpose? *What* is the business information exchanged conceptually (inputs and outputs described in domain terms)?
* **The Design (`design.md`)** defines the physical implementation: *How* is it realized physically? It maps the spec's conceptual inputs/outputs directly to JSON keys, TypeScript interfaces, database schemas, and migration SQL scripts.
* This decoupling allows business rules to remain stable and pure, even as physical technologies, frameworks, or database choices evolve.

### 3. The Unbreakable Quality Loop (Zero-Drift & Traceability)
In SDS, a specification is a **living, executable contract**. 
* **Zero-Drift**: Any modification to a spec's business criteria must trigger corresponding changes in physical code and tests, and vice versa. 
* **Bidirectional Traceability**: Every Gherkin-style Acceptance Criterion (`AC-n`) is physically linked to implementation lines and unit tests using the `@sds-trace` anchor.
* The `sds check` engine statically guarantees this alignment. If a developer introduces an un-documented "stealth feature" or forgets to update tests for a modified requirement, the build fails. This closes the loop between business intent and physical reality.

---

## 📐 SDS Modeling & Organizational Mechanics: The "Dots, Lines, and Planes"

To operationalize SDS as a living human-AI ecosystem, we organize the repository using a cohesive, layered hierarchy that mirrors business domains rather than folder structures:

```text
┌────────────────────────────────────────────────────────┐
│  SYSTEM BLUEPRINT & GLOSSARY (The Plane / 面)          │ <--- High-level business universe
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│  MODULE CONTEXT & JOURNEYS (The Line / 线)             │ <--- End-to-end business lifecycles
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│  CAPABILITY SPEC & DESIGN (The Dot / 点)               │ <--- Atomic transactions & realization
└────────────────────────────────────────────────────────┘
```

### 1. Module vs. Capability
* **The Plane (面 - System Context)**: Global glossaries and the `system-blueprint.md` define the entire boundaries of the business universe.
* **The Line (线 - Module Context)**: High-level business subdomains (e.g., `user_auth`, `billing`) organize cohesive user journeys, business flows, and domain models that span multiple transactional boundaries.
* **The Dot (点 - Capability Spec & Design)**: Atomic, transactional scenarios (e.g., `login`, `refund`) that represent specific business actions.

> [!IMPORTANT]
> **A Capability is NOT a physical API interface/endpoint.** 
> A Capability represents business-value scenarios from the user/product perspective (defined in `spec.md`). A single Capability can be physically realized by multiple API endpoints or polymorphic parameter routes, which are mapped solely in `design.md`. Matching APIs 1-to-1 to Capabilities is an anti-pattern leading to spec fragmentation.

### 2. Hub-and-Spoke: Team Isolation
When multiple teams and projects inside an organization adopt SDS, copying raw validator scripts to every repository is a maintenance nightmare. Instead, we use the **Hub-and-Spoke Model**:

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

* **Zero Harness Bloat**: Spoke repositories do not check in any tooling engine files. Their git trees remain 100% clean and professional.
* **Clean Upgrades**: The core is updated centrally. Projects specify their version in standard dev packages (e.g., `.pre-commit-config.yaml`).

### 3. Separation of Review and Durable Workspace
To avoid cluttering Git with research and temporary files, SDS enforces a strict separation:

* **`specs_review/` (Temporary drafting kitchen)**: Local-only, gitignored directory. This is where you put raw brainstorming, execution plans, technical assessments, diagnostic logs, and verification runtimes.
* **`specs/` (Durable dining room)**: Authoritative, git-tracked directory. Once a design proposal is accepted, the final agreed-upon conclusions are promoted into `specs/` as clean `spec.md`, `design.md` and `_context/` files.

---

## 💖 Heritage & Inspiration: The Future of Software Delivery

Spec-Defined Software (SDS) is proud of its roots and is heavily inspired by and evolved from GitHub's [spec-kit](https://github.com/github/spec-kit) methodology. 

While `spec-kit` pioneered the spec-driven development pattern and introduced rigorous specification validation checks, **the core breakthrough of SDS is organizing the entire specification ecosystem as the future form of software requirement delivery.** 

Rather than just checking text formatting, SDS organizes specifications, boundaries, and designs into a living, multi-dimensional human-AI collaborative environment. By formalizing requirements into traceable business contracts, SDS turns requirements directly into the active, self-correcting structural blueprint of the running software.
