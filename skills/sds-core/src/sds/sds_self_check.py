#!/usr/bin/env python3
"""
SDS (Spec-Defined Software) Cross-Platform Validation Harness
Standard-Library-Only, Cross-Platform (Windows/macOS/Linux) implementation.

This script performs baseline compliance validation for SDS projects:
1. Validates project directory structure and configurations.
2. Checks that specification files are complete and include required sections.
3. Detects code-to-spec drift using Git (monorepo & nested-directory friendly).
4. Performs basic static audit of side effects in code compared to spec frontmatter.
   Includes dedicated scanning for Python, JS/TS, Java, and MyBatis XML Mappers.
5. Verifies traceability down to the specific Acceptance Criteria (AC) level.
6. Generates structured JSON diagnostics on failure for automated self-healing.
7. Runs project-defined verification commands when configured.

Usage:
  python sds_self_check.py                - Run SDS checks
  python sds_self_check.py --init         - Scaffold new SDS directories & templates
  python sds_self_check.py --install-hook - Install Git pre-commit drift guard hook
  python sds_self_check.py --refresh-harness - Safely refresh the project harness
"""

import os
import sys
import re
import json
import shutil
import subprocess
from fnmatch import fnmatch
from pathlib import Path

SDS_MANAGED_HARNESS = True
HARNESS_VERSION = "2026.08.01.2"
DRIFT_GUARDED_EXTENSIONS = {
    ".bash",
    ".cjs",
    ".css",
    ".go",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".jsx",
    ".mjs",
    ".ps1",
    ".py",
    ".rs",
    ".service",
    ".sh",
    ".sql",
    ".svelte",
    ".toml",
    ".ts",
    ".tsx",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
    ".zsh",
}
DRIFT_GUARDED_FILENAMES = {
    "Dockerfile",
    "Makefile",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "pyproject.toml",
    "uv.lock",
    "yarn.lock",
}

# --- CLI Styling ---
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

if sys.platform == "win32":
    os.system("")

def print_info(msg):
    print(f"{COLOR_BLUE}[INFO]{COLOR_RESET} {msg}")

def print_success(msg):
    print(f"{COLOR_GREEN}{COLOR_BOLD}[PASS]{COLOR_RESET} {msg}")

def print_warn(msg):
    print(f"{COLOR_YELLOW}[WARN]{COLOR_RESET} {msg}")

def print_error(msg):
    print(f"{COLOR_RED}{COLOR_BOLD}[FAIL]{COLOR_RESET} {msg}", file=sys.stderr)


# --- Template Definitions for CLI Init ---
DEFAULT_HARNESS_YAML = """# SDS Validation Harness Configuration
project_name: "My SDS Project"
spec_dir: "specs"
review_dir: "specs_review"

# Required sections in every spec.md file to be considered valid
required_sections:
  - "Purpose"
  - "Acceptance criteria"
  - "Interface / contract"

# Defensive Guardrails
enforce_drift_guard: true       # Ensure code/UI changes have corresponding spec updates in the same changeset
enforce_side_effects: true      # Statically check database or external API operations against spec metadata
enforce_traceability: true      # Ensure code features trace back to specs with @sds-trace annotations
enforce_artifact_placement: true # Keep process artifacts in the gitignored review workspace
enforce_module_boundaries: true # Require module _context and path-aligned capability IDs

# Optional project-quality gate. Each command is an argv array and runs without a shell.
# Keep environment-specific deployment/smoke commands in controlled release tooling.
verification_commands: []
# Use "{python}" as the first argument to reuse the interpreter running this harness.

# Stable Markdown names allowed under any specs/**/_context/ directory.
# Add project-specific current-state context names here; assessments still belong in specs_review/.
authoritative_context_files:
  - "system-blueprint.md"
  - "user-journey.md"
  - "business-flow.md"
  - "domain-model.md"
  - "change-history.md"
  - "glossary.md"
  - "deployment-boundary.md"
  - "role-scenario-matrix.md"
  - "README.md"
  - "README.zh.md"
  - "readme.md"
  - "readme.zh.md"
"""

DEFAULT_SPEC_TEMPLATE = """---
capability_id: <module_name>.<capability_name>
status: defined  # options: defined, implemented, deprecated
version: 1.0.0
side_effects:
  database:
    - table: "<table_name>"
      operations: ["select", "insert"]
  external_apis: []
  file_system: []
  browser_storage: []
---

# Capability Specification: <Capability Name>

## 1. Purpose
A concise statement of the business goal. Explain what problem this capability solves for the user, and why it is necessary.

## 2. Acceptance Criteria
Provide a list of verifiable conditions. Keep them clear, atomic, and testable using plain business/domain terms:

- **AC-1**: Given [Precondition] / When [Action] / Then [Expected business outcome]
- **AC-2**: Given [Precondition] / When [Action] / Then [Expected business outcome]
- **AC-3**: Given [Precondition] / When [Action] / Then [Expected business outcome]

## 3. Interface / Contract
Define the machine-readable input and output schemas conceptually.

### A. Business Inputs (Information required to initiate):
- **User Identifier**: The identity of the authenticated user performing the action.
- **Input Item 1**: Explanation of the required business input (e.g. quantity, selected ID).

### B. Business Outputs (Information returned upon completion):
- **Result Status**: Succession or failure of the action from a business perspective.
- **Output Item 1**: Explanation of the business output (e.g. generated order reference).

## 4. Business Rules & Edge Cases
Detailed business constraints, validation rules, and specific edge case behaviors from the user's perspective:

- **Validation Rules**: Minimum lengths, business constraints, valid formats.
- **Error Behavior**: Map specific failure scenarios to user-friendly business descriptions.
- **Rate Limits & Boundaries**: Max/min thresholds, business throttling policies.

## 5. Operational Contract (When Applicable)
Define business-level lifecycle operational goals (e.g., retention, compliance, auditing rules). Keep technical choices (e.g. database schema migrations, deployment scripts, cron setups) in `design.md`.
"""

DEFAULT_DESIGN_TEMPLATE = """---
sds_kind: authoritative-design
capability_id: <module>.<capability_name>
status: accepted
version: 1.0.0
---

# Technical Design Specification: <Capability Name>

## 1. Architectural & Protocol Overview
A high-level technical overview of how this capability will be integrated into the existing system architecture. State the chosen protocols (e.g., REST, gRPC, MQ), gateways, and component topology.

## 2. Business Contract Mapping
Bridge the gaps between the conceptual "Business Information Exchange" in `spec.md` and the physical API schema.

| Spec Information Element | Physical Field Name | Physical Type | Location (Header/Body/Query) | Constraints / Format |
| :--- | :--- | :--- | :--- | :--- |
| **User Identifier** | `userId` | `string` | Header / JWT payload | UUID format |
| **Input Item 1** | `quantity` | `integer` | Body JSON | `>= 1` |
| **Result Status** | `status` | `string` | Body Response JSON | Enum: `SUCCESS`, `FAILED` |
| **Output Item 1** | `orderId` | `string` | Body Response JSON | UUID format |

## 3. Sequence Diagram & Key Workflows
Outline how different components, services, or layers interact to achieve the user flows defined in the capability spec. Use Mermaid syntax for visualization:

```mermaid
sequenceDiagram
  autonumber
  actor User as User/Client
  participant API as API Layer
  participant Service as Service Layer
  participant DB as Database

  User ->> API: Request (with physical payload)
  API ->> Service: Call Business Logic
  Service ->> DB: Select/Insert Query
  DB -->> Service: Record
  Service -->> API: Return Model
  API -->> User: Response
```

## 4. Database Schema & Data Models
Details of new database schemas, migrations, or data modeling adjustments. Outline physical table names, primary keys, indexes, and constraints:

- **New Table/Modifications**: `table_name`
  - `id` (VARCHAR(64), Primary Key)
  - `field_name` (VARCHAR(128), Indexed)

## 5. Detailed API, Routing & Class Design (How)
Detailed classes, functions, controllers, or endpoint routing patterns. Include design patterns, cache strategies, or third-party SDK integration details.

## 6. Non-Functional Requirements & Performance Budgets
- **Response Budget**: e.g., HTTP requests must return in <200ms.
- **Cache Strategy**: e.g., Redis caching with TTL of 5 minutes.
- **Error Handling & Retry Mechanism**: e.g., Backoff retries on transient external API failures.

## 7. Local Code Layout & Source Directories (When Applicable)
- **Source Code Locations**: Paths to the primary editable source code files and directories.
- **Build/Compile Output (If applicable)**: Frontend build directories or local static bundle destinations.
- **Legacy Files & Entrypoints to Retire**: Code files, functions, or modules to delete/retire after implementing this design.

## 8. Local Data Migrations & Schema Evolution (When Applicable)
- **Migration Identity & Sequencing**: Migration/version identifier (e.g. Flyway file or local script timestamp) and its order.
- **Schema Backward/Forward Compatibility**: How the database schema change handles old/new data concurrently without breaking local runtime.
- **Local Rollback Script DDL**: SQL statements or commands to revert the database schema change locally in case of validation failures.

## 9. State Machine & Materialization (When Applicable)
- **Reachability**: Initial/empty, active, terminal, retry, and recovery transitions without circular prerequisites.
- **Truth & Writers**: Authoritative runtime store and single-writer boundaries.
- **Derived Outputs**: Materialization order, rebuildable projections/exports, and compatibility consumers.
- **Completion**: Scheduler ownership, missed-run detection, idempotent retry, backfill, and reconciliation.
"""

# System level context template
DEFAULT_SYSTEM_BLUEPRINT_TEMPLATE = """# System Architectural Blueprint & Module Partitioning
> [!NOTE]
> This system-level context is kept light to map the macro relationship, global integration flows, and boundaries between business modules.

## 1. System Module Boundaries
Describe the system's macro modules and their division of responsibilities:
- **Module A**: Description of core business responsibilities.
- **Module B**: Description of core business responsibilities.

## 2. Global Integration Map
A high-level topology of how business modules communicate with each other (e.g. REST APIs, Event-driven messages, shared schemas):

```mermaid
graph LR
    A[Module A] -->|Capability API| B[Module B]
```
"""

# Module level context templates
DEFAULT_USER_JOURNEY_TEMPLATE = """# Module User Journeys & Scenarios
Outline the complete business scenarios and user journeys hosted within this module.

## Scenario 1: Standard Operational Flow
Describe the entry conditions, user actions, happy path, and alternative/unhappy paths.
"""

DEFAULT_BUSINESS_FLOW_TEMPLATE = """# Module Business Flows & Choreography
Outline the core data orchestration and capabilities choreography boundaries that exist inside this module.

## Flow 1: Inter-Capability Choreography
```mermaid
graph TD
    A[Capability 1] --> B[Capability 2]
    B --> C[Capability 3]
```
"""

DEFAULT_DOMAIN_MODEL_TEMPLATE = """# Module Domain Model & Invariants
Describe the core business entities, aggregates, values, and the invariant rules that govern this module's boundary.

## Core Entities & Invariants
- **Entity Name**: Describe fields, behaviors, constraints, and business-level invariants.
"""

# Ephemeral Plan and Task templates to be scaffolded directly inside specs_review/
DEFAULT_PLAN_TEMPLATE = """# Execution Plan: <Capability Name>
> [!NOTE]
> This is an ephemeral execution plan mapped to `specs_review/<module>/<capability>/plan.md`. It tracks technical phases, milestones, and verification tests. It is Git-ignored.

## 1. Strategy & Risk Assessment
- Core dependencies to establish first.
- Potential technical risks or blocking dependencies.

## 2. Implementation Phases

### Phase 1: Foundation & Interfaces (What)
- [ ] Define API schemas or data structures in code.
- [ ] Run drift validation checks.

### Phase 2: Core Business Logic (How)
- [ ] Implement service methods, parsing logic, and annotations.
- [ ] Implement static tracing `@sds-trace` annotations matching specs.

### Phase 3: Verification & Integration (When)
- [ ] Write spec-derived integration or contract tests using an independent design pass.
- [ ] Confirm local test suite executes and passes.

### Phase 4: Compliance Validation (Audit)
- [ ] Run `python sds_self_check.py` and resolve any side-effects or traceability anomalies.
"""

DEFAULT_TASK_TEMPLATE = """# Active Task: <Current Sub-task Name>
> [!NOTE]
> This is a live task tracking file mapped to `specs_review/<module>/<capability>/task.md`. It tracks sub-steps, active compiler feedback, and local diagnostics logs for the current turn. It is Git-ignored.

## 1. Current Goal
Describe precisely what you are trying to solve or build in this specific turn.

## 2. Targeted Files
- `src/main/../Target.java` (Implementation)
- `src/test/../TargetTest.java` (Verification)

## 3. Checklist & Progress
- [ ] Sub-step 1: Code compiles.
- [ ] Sub-step 2: Custom tests execute and verify compliance.

## 4. Troubleshooting & Compilation Diagnostics Logs
Use this section to dump compiler error traces, stack-overflow answers, dependency problems, and remediation notes.
"""

# Concise repository routing; durable detail belongs in specs/, not here.
DEFAULT_AGENTS_MD = """# Repository agent guide

`specs/` is the behavior source of truth. Start at
`specs/_context/system-blueprint.md`, then read the target module's `_context/`,
capability `spec.md`, and accepted `design.md`.

## Routing

- Route by user scenario and responsibility, not by implementation location.
- Keep project-specific module ownership mappings here.
- Put schema evolution, runtime, and deployment under a system/ops module.

## Boundaries

- Keep only repository routing and non-negotiable constraints in this file; do not duplicate specs.
- Put assessments, plans, diagnostics, and evidence in gitignored `specs_review/`.
- Keep scenario, spec, design, implementation, tests, and release gates aligned.

## Verification

Run `python sds_self_check.py` and the repository's required release checks before handoff.
"""


# --- Config & YAML Parser ---
def _parse_yaml_scalar(value):
    value = value.strip()
    if not value:
        return ""
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith(("[", "{", '"')):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_simple_yaml(content):
    """Parse the indentation-based YAML subset used by SDS config/frontmatter."""
    rows = []
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        rows.append((len(raw_line) - len(raw_line.lstrip(" ")), stripped))

    def parse_node(index, indent):
        is_list = rows[index][1].startswith("- ") or rows[index][1] == "-"
        result = [] if is_list else {}

        while index < len(rows):
            row_indent, text_value = rows[index]
            if row_indent < indent:
                break
            if row_indent > indent:
                raise ValueError(f"unexpected indentation near: {text_value}")

            if is_list:
                if not text_value.startswith("-"):
                    break
                item_text = text_value[1:].strip()
                if not item_text:
                    index += 1
                    if index >= len(rows) or rows[index][0] <= indent:
                        result.append(None)
                    else:
                        child, index = parse_node(index, rows[index][0])
                        result.append(child)
                    continue

                is_quoted = item_text.startswith(("'", '"'))
                if ":" in item_text and not is_quoted:
                    key, raw_value = item_text.split(":", 1)
                    item = {key.strip(): _parse_yaml_scalar(raw_value)}
                    index += 1
                    if index < len(rows) and rows[index][0] > indent:
                        continuation, index = parse_node(index, rows[index][0])
                        if not isinstance(continuation, dict):
                            raise ValueError(f"list mapping continuation must be a mapping: {item_text}")
                        item.update(continuation)
                    result.append(item)
                    continue

                result.append(_parse_yaml_scalar(item_text))
                index += 1
                continue

            if ":" not in text_value:
                raise ValueError(f"expected key/value pair near: {text_value}")
            key, raw_value = text_value.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            index += 1
            if raw_value:
                result[key] = _parse_yaml_scalar(raw_value)
            elif index < len(rows) and rows[index][0] > indent:
                result[key], index = parse_node(index, rows[index][0])
            else:
                result[key] = {}

        return result, index

    if not rows:
        return {}
    parsed, final_index = parse_node(0, rows[0][0])
    if final_index != len(rows) or not isinstance(parsed, dict):
        raise ValueError("top-level YAML value must be a mapping")
    return parsed


def load_config(root_path):
    """Loads SDS configuration from .sds.harness.yaml or defaults."""
    default_config = {
        "project_name": "Unnamed SDS Project",
        "spec_dir": "specs",
        "review_dir": "specs_review",
        "required_sections": ["Purpose", "Acceptance criteria", "Interface / contract"],
        "enforce_drift_guard": True,
        "enforce_side_effects": True,
        "enforce_traceability": True,
        "enforce_artifact_placement": True,
        "enforce_module_boundaries": True,
        "verification_commands": [],
        "authoritative_context_files": [
            "system-blueprint.md",
            "user-journey.md",
            "business-flow.md",
            "domain-model.md",
            "change-history.md",
            "glossary.md",
            "deployment-boundary.md",
            "role-scenario-matrix.md",
            "README.md",
            "README.zh.md",
            "readme.md",
            "readme.zh.md",
        ],
        "ignore_dirs": [
            ".git",
            ".venv",
            "venv",
            "env",
            "node_modules",
            "__pycache__",
            "*.egg-info",
            ".idea",
        ],
    }
    
    config_file = root_path / ".sds.harness.yaml"
    if not config_file.exists():
        return default_config
        
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            parsed = parse_simple_yaml(f.read())
            for k, v in parsed.items():
                default_config[k] = v
        return default_config
    except Exception as e:
        print_warn(f"Failed to parse '.sds.harness.yaml' ({e}). Using standard defaults.")
        return default_config


# --- Markdown & Frontmatter Parsers ---
def parse_spec_file(path):
    """Parses a capability spec.md file, separating YAML frontmatter from the markdown body."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return {}, content
            
        fm_text = match.group(1)
        body = content[match.end():]
        fm_data = parse_simple_yaml(fm_text)
        return fm_data, body
    except Exception as e:
        print_error(f"Error reading spec file {path.name}: {e}")
        return {}, ""


def has_authoritative_context_marker(path):
    """Return whether a nonstandard context file explicitly declares durable state."""
    frontmatter, _ = parse_spec_file(path)
    return frontmatter.get("sds_kind") == "authoritative-context"


def is_ignored_scan_path(path, root_path, config):
    """Return whether a recursive source scan should skip this path."""
    try:
        parts = path.relative_to(root_path).parts
    except ValueError:
        parts = path.parts
    patterns = {
        str(config["spec_dir"]),
        str(config["review_dir"]),
        *[str(item) for item in config.get("ignore_dirs", [])],
    }
    return any(fnmatch(part, pattern) for part in parts for pattern in patterns)


def is_drift_guarded_path(path):
    """Return whether a changed artifact can alter runtime, build, data, or release behavior."""
    return path.name in DRIFT_GUARDED_FILENAMES or path.suffix.lower() in DRIFT_GUARDED_EXTENSIONS


def check_headings(body, required_sections):
    """Checks if required headings are present in the spec body."""
    missing = []
    for section in required_sections:
        pattern = r'^\s*#+\s*(?:\d+\.?\s*)?' + re.escape(section) + r'(?:\s*[:/])?\s*$'
        found = False
        for line in body.splitlines():
            if re.match(pattern, line, re.IGNORECASE):
                found = True
                break
        if not found:
            missing.append(section)
    return missing


def extract_ac_ids(body):
    """
    Statically extracts Acceptance Criteria (AC) IDs from Markdown body.
    Finds list bullet items beginning with identifiers like AC-1, AC-2, etc.
    """
    pattern = r'^\s*(?:#{1,6}\s+|[-*+]\s+)(?:\*\*|\*|__)?(AC-[\w-]+)'
    ac_ids = set()
    for line in body.splitlines():
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            ac_ids.add(match.group(1).upper())
    return ac_ids


def extract_tables_from_sql(sql_content):
    """Extracts database table names from SQL content using strict matching patterns."""
    tables = set()
    patterns = [
        re.compile(r'\bfrom\s+([\w\-\.\`"]+)', re.IGNORECASE),
        re.compile(r'\bjoin\s+([\w\-\.\`"]+)', re.IGNORECASE),
        re.compile(r'\binto\s+([\w\-\.\`"]+)', re.IGNORECASE),
        re.compile(r'\bupdate\s+([\w\-\.\`"]+)', re.IGNORECASE)
    ]
    for pattern in patterns:
        for match in pattern.finditer(sql_content):
            table = match.group(1).strip().strip('`').strip('"').lower()
            if table and table not in ["select", "where", "set", "values", "dual", "left", "right", "inner", "outer"]:
                tables.add(table)
    return tables


# --- Project Initialization & Setup Tool ---
def initialize_sds_project(root_path):
    """Scaffolds all folder directories and drops template files for immediate SDS usage."""
    print_info(f"Initializing SDS workspace under: {COLOR_BOLD}{root_path}{COLOR_RESET}")
    
    spec_dir = root_path / "specs"
    review_dir = root_path / "specs_review"
    system_context_dir = spec_dir / "_context"
    
    # Establish a default module structure
    default_module_dir = spec_dir / "example_module"
    module_context_dir = default_module_dir / "_context"
    default_cap_dir = default_module_dir / "example_capability"
    
    for directory in [spec_dir, review_dir, system_context_dir, default_module_dir, module_context_dir, default_cap_dir]:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print_success(f"Created directory: {directory.relative_to(root_path)}")
            
    harness_path = root_path / ".sds.harness.yaml"
    if not harness_path.exists():
        with open(harness_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_HARNESS_YAML)
        print_success("Created configuration file: .sds.harness.yaml")
    else:
        print_info("File .sds.harness.yaml already exists, skipping.")

    gitignore_path = root_path / ".gitignore"
    gitignore_content = gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""
    if not any(
        line.strip().rstrip("/*") == "specs_review"
        for line in gitignore_content.splitlines()
    ):
        separator = "" if not gitignore_content or gitignore_content.endswith("\n") else "\n"
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write(f"{separator}specs_review/\n")
        print_success("Added specs_review/ to .gitignore.")
        
    # Scaffold a concise routing guide; durable behavior stays in specs/.
    agents_path = next(
        (root_path / name for name in ("AGENTS.md", "agents.md") if (root_path / name).exists()),
        root_path / "AGENTS.md",
    )
    if not agents_path.exists():
        with open(agents_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_AGENTS_MD)
        print_success("Created concise repository routing guide: AGENTS.md")
    else:
        print_info(f"File {agents_path.name} already exists, skipping.")
        
    # Scaffold plan.template.md & task.template.md directly inside specs_review/
    plan_template_path = review_dir / "plan.template.md"
    if not plan_template_path.exists():
        with open(plan_template_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_PLAN_TEMPLATE)
        print_success("Created plan template: specs_review/plan.template.md (recommendation only)")
        
    task_template_path = review_dir / "task.template.md"
    if not task_template_path.exists():
        with open(task_template_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_TASK_TEMPLATE)
        print_success("Created task template: specs_review/task.template.md (recommendation only)")
        
    # Scaffold light system blueprint
    blueprint_path = system_context_dir / "system-blueprint.md"
    if not blueprint_path.exists():
        with open(blueprint_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_SYSTEM_BLUEPRINT_TEMPLATE)
        print_success("Created system blueprint: specs/_context/system-blueprint.md")
        
    spec_template_path = default_cap_dir / "spec.md"
    if not spec_template_path.exists():
        spec_content = DEFAULT_SPEC_TEMPLATE\
            .replace("<module_name>", "example_module")\
            .replace("<capability_name>", "example_capability")\
            .replace("<Capability Name>", "Example Capability")\
            .replace("<table_name>", "example_table")
        with open(spec_template_path, "w", encoding="utf-8") as f:
            f.write(spec_content)
        print_success("Created spec draft: specs/example_module/example_capability/spec.md")
        
    design_template_path = default_cap_dir / "design.md"
    if not design_template_path.exists():
        design_content = DEFAULT_DESIGN_TEMPLATE\
            .replace("<module>", "example_module")\
            .replace("<capability_name>", "example_capability")\
            .replace("<Capability Name>", "Example Capability")
        with open(design_template_path, "w", encoding="utf-8") as f:
            f.write(design_content)
        print_success("Created design draft: specs/example_module/example_capability/design.md")
        
    journey_path = module_context_dir / "user-journey.md"
    if not journey_path.exists():
        with open(journey_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_USER_JOURNEY_TEMPLATE)
        print_success("Created module user-journey: specs/example_module/_context/user-journey.md")
        
    flow_path = module_context_dir / "business-flow.md"
    if not flow_path.exists():
        with open(flow_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_BUSINESS_FLOW_TEMPLATE)
        print_success("Created module business-flow: specs/example_module/_context/business-flow.md")
        
    model_path = module_context_dir / "domain-model.md"
    if not model_path.exists():
        with open(model_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_DOMAIN_MODEL_TEMPLATE)
        print_success("Created module domain-model: specs/example_module/_context/domain-model.md")
        
    print("\n" + "="*50)
    print(f"{COLOR_GREEN}{COLOR_BOLD}SDS Project Initialized Successfully!{COLOR_RESET}")
    print("Under SDS, modules host complete business scenarios, while capabilities provide concrete details.")
    print("Check specs_review/ for ephemeral plan and task templates.")
    print("The root AGENTS.md provides concise routing and repository guardrails.")
    print("Run `python sds_self_check.py` to run verification checks.")
    print("="*50 + "\n")


# --- Git Hook Installer ---
def install_git_hook(root_path):
    """Installs sds_self_check.py as a physical Git pre-commit hook to block invalid changes."""
    git_dir = root_path / ".git"
    if not git_dir.exists():
        print_error("Cannot install Git hook: '.git/' directory not found. Please run `git init` first.")
        sys.exit(1)

    hook_dir = git_dir / "hooks"
    if not hook_dir.exists():
        hook_dir.mkdir(parents=True, exist_ok=True)

    hook_path = hook_dir / "pre-commit"

    hook_content = """#!/bin/sh
# --- SDS (Spec-Defined Software) Pre-Commit Validation Hook ---
echo "Running SDS self-check pre-commit validation..."
python sds_self_check.py
if [ $? -ne 0 ]; then
    echo "=================================================="
    echo "Commit BLOCKED by SDS Drift Guard!"
    echo "Fix the errors in your specifications/implementation before committing."
    echo "=================================================="
    exit 1
fi
exit 0
"""

    try:
        with open(hook_path, "w", encoding="utf-8") as f:
            f.write(hook_content)

        if sys.platform != "win32":
            import stat
            mode = os.stat(hook_path).st_mode
            os.chmod(hook_path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        print_success(f"Git pre-commit hook installed successfully at: {hook_path.relative_to(root_path)}")
    except Exception as e:
        print_error(f"Failed to install Git hook: {e}")
        sys.exit(1)


def refresh_project_harness(root_path):
    """Refresh managed project copies without overwriting customized repository checkers."""
    source_path = Path(__file__).resolve()
    target_path = (root_path / "sds_self_check.py").resolve()
    if source_path == target_path:
        print_info(
            "This is already the project-local harness. Run the skill-owned upstream "
            "script with --refresh-harness to compare a newer version."
        )
        return 0

    if not target_path.exists():
        shutil.copy(source_path, target_path)
        print_success(f"Installed managed SDS harness {HARNESS_VERSION}: sds_self_check.py")
        return 0

    target_content = target_path.read_text(encoding="utf-8", errors="ignore")
    source_content = source_path.read_text(encoding="utf-8")
    if target_content == source_content:
        print_success(f"Project harness is current: {HARNESS_VERSION}")
        return 0

    if "SDS_MANAGED_HARNESS = True" in target_content:
        shutil.copy(source_path, target_path)
        print_success(f"Refreshed managed SDS harness to {HARNESS_VERSION}")
        return 0

    review_dir = root_path / load_config(root_path)["review_dir"]
    review_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = review_dir / "sds_self_check.upstream.py"
    shutil.copy(source_path, candidate_path)
    print_warn(
        "Project sds_self_check.py is customized and was not overwritten. "
        f"Merge relevant upstream changes from {candidate_path.relative_to(root_path)}."
    )
    return 2


# --- Validation Logic ---
def validate_sds(root_path):
    config = load_config(root_path)
    
    spec_dir = root_path / config["spec_dir"]
    review_dir = root_path / config["review_dir"]
    
    errors = []
    
    # --- 1. Structure Check ---
    print_info("Step 1: Checking workspace directories...")
    if not spec_dir.exists():
        errors.append({
            "code": "MISSING_SPEC_DIR",
            "severity": "error",
            "target": str(config["spec_dir"]),
            "message": f"Specifications directory '{config['spec_dir']}' does not exist in the project root.",
            "remediation_hint": "Run `python sds_self_check.py --init` to automatically scaffold the directory structure."
        })
        
    if not review_dir.exists():
        try:
            review_dir.mkdir(parents=True, exist_ok=True)
            print_info(f"Created missing review directory: '{config['review_dir']}'")
        except Exception as e:
            errors.append({
                "code": "MISSING_REVIEW_DIR",
                "severity": "error",
                "target": str(config["review_dir"]),
                "message": f"Unable to create review directory '{config['review_dir']}': {e}",
                "remediation_hint": f"Create a '{config['review_dir']}/' directory manually."
            })

    if errors:
        write_diagnostics_and_exit(review_dir, errors)

    if config.get("enforce_artifact_placement", True):
        try:
            repo_result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=root_path,
                capture_output=True,
                text=True,
            )
            if repo_result.returncode == 0:
                ignored_probe = review_dir / ".sds-ignore-probe"
                ignore_result = subprocess.run(
                    ["git", "check-ignore", "--quiet", "--", str(ignored_probe.relative_to(root_path))],
                    cwd=root_path,
                    capture_output=True,
                    text=True,
                )
                if ignore_result.returncode != 0:
                    errors.append({
                        "code": "REVIEW_DIR_NOT_GITIGNORED",
                        "severity": "error",
                        "target": str(review_dir.relative_to(root_path)),
                        "message": "The SDS process-artifact directory is not ignored by Git.",
                        "remediation_hint": f"Add '{review_dir.name}/' to .gitignore so assessments and diagnostics are not tracked.",
                    })
            else:
                print_warn("Git ignore verification skipped because the project is not a Git worktree.")
        except (OSError, ValueError):
            print_warn("Could not verify that the review directory is ignored by Git.")

        allowed_context_files = {
            str(name).strip()
            for name in config.get("authoritative_context_files", [])
            if str(name).strip()
        }
        for context_path in spec_dir.rglob("*.md"):
            if "_context" not in context_path.parts:
                continue
            if context_path.name in allowed_context_files:
                continue
            if has_authoritative_context_marker(context_path):
                continue
            rel_context_path = context_path.relative_to(root_path)
            errors.append({
                "code": "UNCLASSIFIED_CONTEXT_ARTIFACT",
                "severity": "error",
                "target": str(rel_context_path),
                "message": (
                    f"Nonstandard context document '{rel_context_path}' is not classified "
                    "as accepted authoritative state."
                ),
                "remediation_hint": (
                    f"Move assessments, proposals, audits, plans, and gap analyses to "
                    f"'{review_dir.name}/'. If this is durable current-state context, add its "
                    "filename to authoritative_context_files or declare "
                    "'sds_kind: authoritative-context' frontmatter."
                ),
            })

        review_link_pattern = re.compile(
            rf"\]\([^)]*{re.escape(review_dir.name)}(?:/|\\)[^)]*\)",
            re.IGNORECASE,
        )
        for durable_path in spec_dir.rglob("*.md"):
            try:
                durable_content = durable_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if not review_link_pattern.search(durable_content):
                continue
            rel_durable_path = durable_path.relative_to(root_path)
            errors.append({
                "code": "DURABLE_DOC_LINKS_EPHEMERAL_ARTIFACT",
                "severity": "error",
                "target": str(rel_durable_path),
                "message": (
                    f"Durable document '{rel_durable_path}' links to the gitignored "
                    f"'{review_dir.name}/' workspace."
                ),
                "remediation_hint": (
                    "Move the accepted conclusion into the durable document and remove "
                    "the link to the process artifact."
                ),
            })

        if errors:
            write_diagnostics_and_exit(review_dir, errors)

    # --- 2. Context & Specs Audit ---
    print_info("Step 2: Auditing context layers & capability specs...")
    
    specs_found = []
    frontmatters = {}
    spec_to_acs = {}
    spec_to_status = {}
    cap_to_spec_file = {}
    checked_module_contexts = set()
    
    for path in spec_dir.rglob("*.md"):
        if "_context" in path.parts:
            continue
        if path.name in ["spec.template.md", "design.template.md"]:
            continue
        if path.name.lower() == "spec.md":
            specs_found.append(path)
            
    if not specs_found:
        print_warn(f"No active 'spec.md' capability specifications found under '{config['spec_dir']}/'.")
    else:
        print_info(f"Found {len(specs_found)} capability specification(s). Starting deep validation...")
        for spec_path in specs_found:
            rel_spec_path = spec_path.relative_to(root_path)
            rel_spec_tree_path = spec_path.relative_to(spec_dir)
            fm, body = parse_spec_file(spec_path)
            frontmatters[str(rel_spec_path)] = fm
            
            cap_id = fm.get("capability_id")
            if config.get("enforce_module_boundaries", True):
                path_parts = rel_spec_tree_path.parts
                if len(path_parts) != 3:
                    errors.append({
                        "code": "INVALID_CAPABILITY_SPEC_PATH",
                        "severity": "error",
                        "target": str(rel_spec_path),
                        "message": (
                            "Capability specs must use specs/<module>/<capability>/spec.md."
                        ),
                        "remediation_hint": (
                            "Route the capability by user scenario and ownership, then move it "
                            "under the owning module and capability directory."
                        ),
                    })
                else:
                    module_name, capability_name, _ = path_parts
                    module_context_dir = spec_dir / module_name / "_context"
                    if (
                        module_name not in checked_module_contexts
                        and (
                            not module_context_dir.is_dir()
                            or not any(module_context_dir.glob("*.md"))
                        )
                    ):
                        errors.append({
                            "code": "MISSING_MODULE_CONTEXT",
                            "severity": "error",
                            "target": str((spec_dir / module_name).relative_to(root_path)),
                            "message": (
                                f"Module '{module_name}' owns capabilities but has no Markdown "
                                "context under its _context/ directory."
                            ),
                            "remediation_hint": (
                                "Add accepted module journeys/boundaries under "
                                f"'{config['spec_dir']}/{module_name}/_context/' before maintaining capabilities."
                            ),
                        })
                    checked_module_contexts.add(module_name)
                    expected_capability_id = f"{module_name}.{capability_name}"
                    if cap_id and cap_id != expected_capability_id:
                        errors.append({
                            "code": "CAPABILITY_PATH_MISMATCH",
                            "severity": "error",
                            "target": str(rel_spec_path),
                            "message": (
                                f"Capability ID '{cap_id}' does not match its owning path "
                                f"('{expected_capability_id}')."
                            ),
                            "remediation_hint": (
                                "Resolve ownership from the scenario and system blueprint, then "
                                "align both the directory and capability_id."
                            ),
                        })
            if not cap_id:
                errors.append({
                    "code": "MISSING_SPEC_METADATA",
                    "severity": "error",
                    "target": str(rel_spec_path),
                    "message": "Spec is missing 'capability_id' frontmatter metadata.",
                    "remediation_hint": "Add 'capability_id: <module_name>.<capability_name>' to the frontmatter of this file."
                })
            else:
                cap_to_spec_file[cap_id] = str(rel_spec_path)
                spec_to_status[cap_id] = fm.get("status", "").lower()
                
            missing_headers = check_headings(body, config["required_sections"])
            if missing_headers:
                errors.append({
                    "code": "INCOMPLETE_SPECIFICATION",
                    "severity": "error",
                    "target": str(rel_spec_path),
                    "message": f"Spec is missing required section headings: {', '.join(missing_headers)}",
                    "remediation_hint": f"Add proper headers (e.g. '## {missing_headers[0]}') to the markdown file."
                })
                
            if cap_id:
                acs = extract_ac_ids(body)
                spec_to_acs[cap_id] = acs
                
            print_success(f"Spec validated: {rel_spec_path}")

    # --- 3. Git Drift Guard ---
    if config["enforce_drift_guard"]:
        print_info("Step 3: Running Git Drift-Guard audit...")
        drift_results, drift_err = check_git_drift(root_path, config["spec_dir"])
        if drift_err:
            print_warn(f"Git Drift-Guard skipped: {drift_err}")
        elif drift_results:
            modified_code = drift_results["modified_code"]
            modified_specs = drift_results["modified_specs"]
            
            if modified_code and not modified_specs:
                errors.append({
                    "code": "DRIFT_DETECTED",
                    "severity": "error",
                    "target": ", ".join(modified_code[:3]),
                    "message": f"Modified implementation files {modified_code[:3]} found, but no specification files in '{config['spec_dir']}/' were changed in this changeset.",
                    "remediation_hint": "Always update the corresponding capability spec.md alongside code changes to preserve specifications as the single source of truth."
                })
            else:
                print_success("Git Drift-Guard passed (specs and code changes are aligned).")
        else:
            print_success("Git Drift-Guard passed (no changes detected).")

    # --- 4. Deep Traceability & AC Alignment Check ---
    if config["enforce_traceability"] and specs_found:
        print_info("Step 4: Running detailed Traceability and AC alignment verification...")
        
        trace_pattern = re.compile(r'@sds-trace:\s*([\w\-\.]+)(?::([\w\-]+))?')
        traced_acs = {cap_id: set() for cap_id in spec_to_acs}
        
        for path in root_path.rglob("*"):
            if path.is_file() and any(path.name.endswith(ext) for ext in [".py", ".js", ".ts", ".html", ".go", ".rs", ".css", ".java", ".xml"]):
                if is_ignored_scan_path(path, root_path, config):
                    continue
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            for match in trace_pattern.finditer(line):
                                cap_id = match.group(1)
                                ac_id = match.group(2)
                                
                                rel_code_file = str(path.relative_to(root_path))
                                
                                if cap_id not in spec_to_acs:
                                    errors.append({
                                        "code": "INVALID_TRACE_CAPABILITY",
                                        "severity": "error",
                                        "target": f"{rel_code_file}:L{line_num}",
                                        "message": f"Code references trace ID '{cap_id}' which matches no active capability spec.",
                                        "remediation_hint": "Verify the capability_id name in your spec frontmatters and match it in code annotations."
                                    })
                                    continue
                                    
                                if ac_id:
                                    ac_upper = ac_id.upper()
                                    defined_acs = spec_to_acs[cap_id]
                                    if ac_upper not in defined_acs:
                                        spec_file_origin = cap_to_spec_file.get(cap_id)
                                        errors.append({
                                            "code": "INVALID_TRACE_AC",
                                            "severity": "error",
                                            "target": f"{rel_code_file}:L{line_num}",
                                            "message": f"Code traces to '{cap_id}:{ac_id}', but '{ac_id}' is not defined in spec: '{spec_file_origin}'.",
                                            "remediation_hint": f"Ensure your spec markdown lists '- **{ac_upper}**' as an atomic bullet item."
                                        })
                                    else:
                                        traced_acs[cap_id].add(ac_upper)
                except Exception as e:
                    print_warn(f"Failed to scan file {path} for traceability: {e}")
                    
        # Verify trace coverage for all implemented/verified specs
        for cap_id, defined_acs in spec_to_acs.items():
            status = spec_to_status.get(cap_id, "")
            if status in ["implemented", "verified"]:
                uncovered_acs = defined_acs - traced_acs[cap_id]
                if uncovered_acs:
                    spec_file_origin = cap_to_spec_file.get(cap_id)
                    errors.append({
                        "code": "MISSING_TRACE_COVERAGE",
                        "severity": "error",
                        "target": spec_file_origin,
                        "message": f"Capability '{cap_id}' is marked as '{status}', but is missing `@sds-trace` annotations for: {', '.join(sorted(uncovered_acs))}.",
                        "remediation_hint": f"Add matching `# @sds-trace: {cap_id}:AC-n` comments above the implementation lines or tests."
                    })
                    
        if not any(e["code"] in ["INVALID_TRACE_CAPABILITY", "INVALID_TRACE_AC", "MISSING_TRACE_COVERAGE"] for e in errors):
            print_success("Traceability & AC alignment verification passed.")

    # --- 5. Side-Effects Static Audit (Including Java & MyBatis support) ---
    if config["enforce_side_effects"] and specs_found:
        print_info("Step 5: Statically auditing code side-effects...")
        allowed_domains = set()
        allowed_tables = set()
        
        for spec_path, fm in frontmatters.items():
            side_effects = fm.get("side_effects", {})
            if isinstance(side_effects, dict):
                # External APIs
                external_apis = side_effects.get("external_apis", [])
                if isinstance(external_apis, list):
                    for api in external_apis:
                        if isinstance(api, dict) and "domain" in api:
                            allowed_domains.add(api["domain"].lower())
                        elif isinstance(api, str):
                            allowed_domains.add(api.lower())
                # Database tables
                db_elements = side_effects.get("database", [])
                if isinstance(db_elements, list):
                    for db_el in db_elements:
                        if isinstance(db_el, dict) and "table" in db_el:
                            allowed_tables.add(db_el["table"].lower())
                        elif isinstance(db_el, str):
                            allowed_tables.add(db_el.lower())

        # Regex patterns
        url_pattern = re.compile(r'https?://([\w\-\.]+)')
        feign_pattern = re.compile(r'@FeignClient\([^)]*url\s*=\s*["\'](https?://[^"\']+)["\']', re.IGNORECASE)
        jdbc_pattern = re.compile(r'jdbc:(mysql|postgresql|oracle|sqlserver|sqlite|mariadb|db2)://([\w\-\.:]+)/([\w\-]+)', re.IGNORECASE)
        mybatis_anno_pattern = re.compile(r'@(Select|Insert|Update|Delete)\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE)

        for path in root_path.rglob("*"):
            if path.is_file() and any(path.name.endswith(ext) for ext in [".py", ".js", ".ts", ".java", ".xml"]):
                if is_ignored_scan_path(path, root_path, config):
                    continue
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        
                    rel_file_path = str(path.relative_to(root_path))
                        
                    # 5.2 General External Domain Audit (across all languages)
                    for match in url_pattern.finditer(content):
                        domain = match.group(1).lower()
                        if domain in ["localhost", "127.0.0.1", "0.0.0.0"]:
                            continue
                        if domain not in allowed_domains:
                            if any(trigger in domain for trigger in ["api", "stripe", "aws", "gcp", "azure"]):
                                errors.append({
                                    "code": "UNAUTHORIZED_SIDE_EFFECT",
                                    "severity": "error",
                                    "target": rel_file_path,
                                    "message": f"Code references unauthorized external API domain: '{domain}'.",
                                    "remediation_hint": f"Explicitly declare '{domain}' under 'side_effects.external_apis' in your capability spec.md."
                                })
                                
                    # 5.3 MyBatis Mapper XML static validation
                    if path.name.endswith(".xml") and "<mapper" in content:
                        if not allowed_tables:
                            errors.append({
                                "code": "UNAUTHORIZED_SIDE_EFFECT",
                                "severity": "error",
                                "target": rel_file_path,
                                "message": "MyBatis Mapper XML file defined, but active specs declare no database side-effects.",
                                "remediation_hint": "Add authorized database tables under 'side_effects.database' in your capability spec.md."
                            })
                        else:
                            sql_tags = re.findall(r'<(select|insert|update|delete)[^>]*>(.*?)</\1>', content, re.DOTALL | re.IGNORECASE)
                            for tag, sql_body in sql_tags:
                                tables = extract_tables_from_sql(sql_body)
                                for table in tables:
                                    if table not in allowed_tables:
                                        errors.append({
                                            "code": "UNAUTHORIZED_SIDE_EFFECT",
                                            "severity": "error",
                                            "target": rel_file_path,
                                            "message": f"MyBatis Mapper XML defines a <{tag}> query operating on unauthorized table '{table}'.",
                                            "remediation_hint": f"Explicitly declare table '{table}' under 'side_effects.database' in your capability spec.md."
                                        })
                                
                    # 5.4 Java-Specific Audit Points
                    if path.name.endswith(".java"):
                        for match in feign_pattern.finditer(content):
                            url = match.group(1)
                            domain_match = re.match(r'https?://([\w\-\.]+)', url)
                            if domain_match:
                                domain = domain_match.group(1).lower()
                                if domain not in allowed_domains:
                                    errors.append({
                                        "code": "UNAUTHORIZED_SIDE_EFFECT",
                                        "severity": "error",
                                        "target": rel_file_path,
                                        "message": f"Java @FeignClient references unauthorized external API domain: '{domain}'.",
                                        "remediation_hint": f"Explicitly declare '{domain}' under 'side_effects.external_apis' in your capability spec.md."
                                    })
                                    
                        for match in jdbc_pattern.finditer(content):
                            db_type = match.group(1)
                            db_name = match.group(3).lower()
                            
                            has_db_declaration = False
                            for s_path, fm in frontmatters.items():
                                db_declared = fm.get("side_effects", {}).get("database", [])
                                if db_declared:
                                    has_db_declaration = True
                                    break
                                    
                            if not has_db_declaration:
                                errors.append({
                                    "code": "UNAUTHORIZED_SIDE_EFFECT",
                                    "severity": "error",
                                    "target": rel_file_path,
                                    "message": f"Java code hardcodes a JDBC connection to database '{db_name}' ({db_type}), but active specs declare no database side-effects.",
                                    "remediation_hint": "Declare the authorized database tables under 'side_effects.database' in your capability spec.md frontmatter."
                                })
                                
                        for match in mybatis_anno_pattern.finditer(content):
                            operation = match.group(1)
                            sql_query = match.group(2)
                            
                            if not allowed_tables:
                                errors.append({
                                    "code": "UNAUTHORIZED_SIDE_EFFECT",
                                    "severity": "error",
                                    "target": rel_file_path,
                                    "message": f"Java method uses MyBatis @{operation} annotation, but active specs declare no database side-effects.",
                                    "remediation_hint": "Add 'database' entries under 'side_effects' in your capability spec.md."
                                })
                            else:
                                tables = extract_tables_from_sql(sql_query)
                                for table in tables:
                                    if table not in allowed_tables:
                                        errors.append({
                                            "code": "UNAUTHORIZED_SIDE_EFFECT",
                                            "severity": "error",
                                            "target": rel_file_path,
                                            "message": f"Java MyBatis annotation @{operation} operates on unauthorized table '{table}'.",
                                            "remediation_hint": f"Explicitly declare table '{table}' under 'side_effects.database' in your capability spec.md."
                                        })
                except Exception:
                    pass
        
        if not any(e["code"] == "UNAUTHORIZED_SIDE_EFFECT" for e in errors):
            print_success("Static side-effects audit passed.")

    # --- 6. Project-defined verification commands ---
    verification_commands = config.get("verification_commands", [])
    if verification_commands is None:
        verification_commands = []
    if not isinstance(verification_commands, list):
        errors.append({
            "code": "INVALID_VERIFICATION_COMMANDS",
            "severity": "error",
            "target": ".sds.harness.yaml:verification_commands",
            "message": "verification_commands must be a list of non-empty argv arrays.",
            "remediation_hint": (
                "Use entries such as ['python', '-m', 'pytest', 'tests/']; "
                "commands run directly without a shell."
            ),
        })
    elif verification_commands and not errors:
        print_info("Step 6: Running project-defined verification commands...")
        for index, command in enumerate(verification_commands):
            target = f".sds.harness.yaml:verification_commands[{index}]"
            if (
                not isinstance(command, list)
                or not command
                or not all(isinstance(argument, str) and argument for argument in command)
            ):
                errors.append({
                    "code": "INVALID_VERIFICATION_COMMAND",
                    "severity": "error",
                    "target": target,
                    "message": "Each verification command must be a non-empty argv array of strings.",
                    "remediation_hint": (
                        "Use an argv array such as ['npm', 'run', 'build']; "
                        "do not use shell operators or place secrets in arguments."
                    ),
                })
                continue
            resolved_command = [
                sys.executable if argument == "{python}" else argument
                for argument in command
            ]
            command_name = Path(resolved_command[0]).name
            print_info(f"Running configured verification #{index + 1}: {command_name}")
            try:
                result = subprocess.run(resolved_command, cwd=root_path)
            except OSError as exc:
                errors.append({
                    "code": "VERIFICATION_COMMAND_UNAVAILABLE",
                    "severity": "error",
                    "target": target,
                    "message": f"Unable to start verification command '{command_name}': {exc}",
                    "remediation_hint": "Install or configure the required project tool, then rerun the SDS check.",
                })
                continue
            if result.returncode != 0:
                errors.append({
                    "code": "PROJECT_VERIFICATION_FAILED",
                    "severity": "error",
                    "target": target,
                    "message": (
                        f"Configured verification #{index + 1} ('{command_name}') exited "
                        f"with status {result.returncode}."
                    ),
                    "remediation_hint": "Fix the reported project test/build failure and rerun the SDS check.",
                })
            else:
                print_success(f"Configured project verification #{index + 1} passed: {command_name}")
    elif not verification_commands:
        print_warn(
            "No project verification_commands are configured; SDS baseline checks do not "
            "replace the repository's tests, lint/type checks, builds, or release smoke checks."
        )
    else:
        print_warn("Project verification commands were skipped because SDS baseline checks failed.")

    write_diagnostics_and_exit(review_dir, errors)


def check_git_drift(root_path, spec_dir_name):
    """Executes git commands to determine modified files in code vs specifications."""
    try:
        res_test = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root_path, capture_output=True, text=True)
        if res_test.returncode != 0:
            return None, "Not a Git repository."
            
        res_git_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root_path, capture_output=True, text=True)
        if res_git_root.returncode != 0:
            return None, "Failed to find Git repository root."
        git_root = Path(res_git_root.stdout.strip()).resolve()
        
        res_diff = subprocess.run(["git", "diff", "HEAD", "--name-only"], cwd=root_path, capture_output=True, text=True)
        modified_files = [line.strip() for line in res_diff.stdout.splitlines() if line.strip()]
        
        res_status = subprocess.run(["git", "status", "--porcelain"], cwd=root_path, capture_output=True, text=True)
        if res_status.returncode == 0:
            for line in res_status.stdout.splitlines():
                if line.startswith("?? "):
                    modified_files.append(line[3:].strip())
                    
        if not modified_files:
            return {}, None
            
        code_files = []
        spec_files = []
        
        abs_root_path = root_path.resolve()
        
        for f in modified_files:
            abs_file_path = (git_root / f).resolve()
            
            # Check if this file is actually under our project root_path
            try:
                rel_to_project = abs_file_path.relative_to(abs_root_path)
            except ValueError:
                # File is outside this local project, skip it!
                continue
                
            parts = rel_to_project.parts
            
            if parts and parts[0] == spec_dir_name:
                spec_files.append(str(rel_to_project))
            elif is_drift_guarded_path(rel_to_project):
                if rel_to_project.name == "sds_self_check.py":
                    continue
                code_files.append(str(rel_to_project))
                
        return {
            "modified_code": code_files,
            "modified_specs": spec_files
        }, None
    except Exception as e:
        return None, f"Failed to execute git analysis: {e}"


def write_diagnostics_and_exit(review_dir, errors):
    """Writes the diagnostics.json file and exits with appropriate status code."""
    diag_file = review_dir / "diagnostics.json"
    
    if not errors:
        if diag_file.exists():
            try:
                diag_file.unlink()
            except Exception:
                pass
        print("\n" + "="*50)
        print(
            f"{COLOR_GREEN}{COLOR_BOLD}SDS BASELINE PASSED! "
            f"Repository policy checks and configured project verifications passed.{COLOR_RESET}"
        )
        print("="*50 + "\n")
        sys.exit(0)
    else:
        timestamp = "2026-07-13T00:00:00Z"
        try:
            res_date = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True)
            if res_date.returncode == 0:
                timestamp = res_date.stdout.strip()
        except Exception:
            pass
            
        diag_output = {
            "timestamp": timestamp,
            "status": "failed",
            "errors": errors
        }
        
        try:
            with open(diag_file, "w", encoding="utf-8") as f:
                json.dump(diag_output, f, indent=2, ensure_ascii=False)
            print_info(f"Diagnostic details written to '{review_dir.name}/diagnostics.json'.")
        except Exception as e:
            print_warn(f"Failed to write diagnostic file: {e}")
            
        print("\n" + "="*50)
        print(f"{COLOR_RED}{COLOR_BOLD}SDS CHECK FAILED! {len(errors)} issues detected.{COLOR_RESET}")
        for err in errors:
            print(f"- {COLOR_BOLD}[{err['code']}]{COLOR_RESET} {err['message']}")
            print(f"  Target: {err['target']}")
            print(f"  Remediation: {err['remediation_hint']}")
        print("="*50 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    cwd_path = Path.cwd()
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "--init":
            initialize_sds_project(cwd_path)
            sys.exit(0)
        elif arg == "--install-hook":
            install_git_hook(cwd_path)
            sys.exit(0)
        elif arg == "--refresh-harness":
            sys.exit(refresh_project_harness(cwd_path))
        elif arg == "--version":
            print(HARNESS_VERSION)
            sys.exit(0)
        else:
            print_error(f"Unknown argument: {sys.argv[1]}")
            print("Usage:")
            print("  python sds_self_check.py                - Run SDS checks")
            print("  python sds_self_check.py --init         - Scaffold new SDS directories & templates")
            print("  python sds_self_check.py --install-hook - Install Git pre-commit drift guard hook")
            print("  python sds_self_check.py --refresh-harness - Safely refresh the project harness")
            print("  python sds_self_check.py --version      - Print upstream harness version")
            sys.exit(1)
            
    validate_sds(cwd_path)
