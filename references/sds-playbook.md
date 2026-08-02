# SDS Playbook & User Manual / SDS 使用手册

This manual provides a detailed step-by-step guide for developers, product managers, and AI agents on how to use Spec-Defined Software (SDS) for requirement delivery.
本手册为开发人员、产品经理和 AI 代理提供了一份详细的逐步指南，指导如何使用规范定义软件 (SDS) 进行需求交付。

---

## 1. AI Interactive Commands (`/sds`) / AI 交互指令快速上手

As an AI-Native development paradigm, SDS is completely driven through natural language **AI Commands (AI 交互指令)** rather than manual script execution. You do not need to run terminal scripts or manually structure complex files. Simply issue standard commands in chat to your AI Agent to automate the complete requirement delivery cycle:
作为 AI 原生（AI-Native）的开发范式，SDS 完全通过自然语言的 **AI 交互指令** 驱动，而非传统的手动脚本执行。您无需在终端运行繁杂的命令或手动搭建复杂文件，只需在聊天中向您的 AI 代理发送标准指令，即可自动闭环整个需求交付周期：

> [!IMPORTANT]
> **Difference between AI Chat Commands and Terminal CLI Commands / AI 聊天指令与终端 CLI 命令的区别**
> - **AI Chat Commands (AI 聊天指令)**: Commands starting with `/sds ...` (e.g., `/sds analyze`, `/sds implement`, `/sds verify`, `/sds heal`) are high-level **Slash Prompts** designed to be typed directly into your AI assistant chat window to instruct your agentic coding assistant. They are **NOT** terminal shell commands.
> - **Terminal CLI Commands (终端 CLI 命令)**: Commands starting with `sds ...` (e.g., `sds check`, `sds init`, `sds install-hook`) are physical executable binaries that run directly in your local terminal or CI/CD pipelines.
> 
> - **AI 聊天指令**：以 `/sds ...` 开头的指令（如 `/sds analyze`、`/sds implement` 等）是高级**聊天快捷 Prompts**，设计用于在 AI 助手聊天窗口中输入以命令 Agent。它们**不是**在终端执行的 Shell 命令。
> - **终端 CLI 命令**：以 `sds ...` 开头的命令（如 `sds check`、`sds init` 等）是实体二进制可执行命令，运行在您的本地终端或 CI/CD 管道中。

### 1.1 The Standard AI Command Set / SDS 标准 AI 指令集

| AI Command / AI 指令 | Action & Description / 核心作用与行为 | Behind-the-scenes Agent Task / AI 后台执行任务 |
| :--- | :--- | :--- |
| **`/sds init`** | **Initialize SDS skeleton** / 初始化 SDS 骨架 | Runs `--init` to scaffold `specs/`, `.gitignore` & configs. |
| **`/sds analyze <User Scenario>`** | **Analyze User Scenario** / 需求场景分析 | Refines raw user scenario into Gherkin ACs & drafts in `specs_review/`. |
| **`/sds implement`** | **Implement requirement** / 一键实现需求 | Promotes drafts to `specs/`, writes code/tests with `@sds-trace` tags. |
| **`/sds verify`** | **Verify compliance & zero-drift** / 质量验证 | Runs local checks & test commands to ensure 100% compliance. |
| **`/sds heal`** | **Diagnose & Auto-Repair** / 自动修复故障 | Parses diagnostics to heal code-to-spec drifts or test failures. |

---

### 1.2 The 4-Step Interactive Loop / 极简 4 步交互闭环演示

#### 1️⃣ Step 1: User Scenario Input (`/sds analyze`) / 步骤一：用户场景输入
The PM, PO, or Developer triggers a new requirement by providing a raw user scenario:
PM、PO 或开发人员通过提供一个真实的用户/业务场景来触发新需求：

```text
/sds analyze User Scenario: "Our users find it tedious to remember passwords and want to sign in instantly using their existing Google accounts to save time."
/sds analyze 用户场景：“我们的用户觉得记住密码非常繁琐，希望能够直接使用现有的 Google 账号瞬间登录以节省时间。”
```

#### 2️⃣ Step 2: Agent Automatically Drafts & Reviews / 步骤二：AI 自动分析并起草
The AI Agent automatically identifies whether this is a **new capability** or an **existing capability evolution** (evolving `user_auth/login`).
It automatically writes draft updates inside `specs_review/` and presents a high-level summary of the product ACs and physical mappings in the chat:
AI 代理自动识别这是**全新功能创建**还是**已有能力演进**（本例中为演进 `user_auth/login`）。它会自动在 `specs_review/` 中起草更新，并在聊天中向开发人员呈现极简的直观方案摘要：

```text
📋 [SDS Draft Created / 方案起草完成]
- Module / 业务模块: user_auth
- Capability / 业务能力: login (Evolving / 正在原地演进)

💡 Product Acceptance Criteria (AC) Added / 新增产品验收条件:
  - AC-3: User successfully logs in via valid Google OAuth token.
  - AC-3: 用户通过合法的 Google OAuth Token 成功登录。

🛠️ Technical physical contract mapping updated / 技术接口映射更新:
  - Input payload maps `google_token` (String, Optional) to `/api/v1/auth/login`.

👉 Ready to implement? Please reply "/sds implement" or click the button.
👉 准备好开始实现了吗？请回复 "/sds implement" 或点击一键执行。
```

#### 3️⃣ Step 3: One-Click Implementation (`/sds implement`) / 步骤三：一键实现需求
The developer simply issues the implementation command:
开发人员只需简单发送一键实现指令：

```text
/sds implement
```

The AI Agent automatically:
- Promotes the accepted drafts from `specs_review/` to `specs/` as durable contracts.
- Generates the real backend code/API implementations in `/src`.
- Generates standard automated test cases (e.g. `tests/test_login.py`) tracing back to the new AC.
- Injects tracing markers `@sds-trace: login:AC-3` directly into the code and test files.

AI 代理会自动：
- 将通过的草稿从 `specs_review/` **自动晋级**到 `specs/` 目录中存为持久契约。
- 自动在 `/src` 下生成真实的业务后端代码和 API 实现。
- 自动生成对应的标准测试用例（如 `tests/test_login.py`）对接新的验收条件。
- 在代码 and 测试文件的关键边界自动植入 `@sds-trace: login:AC-3` 溯源标签。

#### 4️⃣ Step 4: Verification & Delivery (`/sds verify`) / 步骤四：自动校验与交付
The Agent automatically executes the verification task in the background:
AI 代理自动在后台调用自检器与项目验证：

```text
Behind-the-scenes task: Runs sds_self_check.py & project unit tests.
后台执行任务：调用 sds_self_check.py 自检与项目单元测试。
```

Once all tests and zero-drift checks return green, the Agent delivers the completed requirement:
校验通过后，AI 代理向您交付结果：

```text
✅ [Requirement Delivered / 需求顺利交付!]
- Specs & Technical Designs successfully updated and promoted under specs/.
- Source code and pytest suites implemented with 100% AC traceability (@sds-trace).
- Local SDS validation (zero-drift checks) returned 100% success.
```

---

## 2. Guidelines for Analyzing User Scenarios / 用户场景分析与规约化指导建议

To deliver high-quality business specifications, follow these guiding principles when capturing, refining, and defining User Scenarios:
为了交付高质量的业务规约，在捕获、提炼和定义用户场景时，请遵循以下指导原则：

### 2.1 Focus on the "Who, What & Why" / 聚焦“人、事、因”
- A raw scenario must clearly answer: **Who** is the user? **What** do they need to achieve? **Why** is it valuable to them?
  一个原始场景必须清晰地回答：**谁**是目标用户？他们需要**达成什么目的**？这**为什么**对他们有价值？
- *Poor Input / 错误输入*: `Add a Google SSO login API and a google_id column.` (This is a technical implementation, not a user scenario).
  *Good Input / 正确输入*: `Our users find it tedious to remember passwords and want to sign in instantly using their existing Google accounts to save time.`
- *避开误区*：不要将具体技术方案（如“加一个字段”、“写一个 API”）作为起点。技术是满足用户场景的衍生物。

### 2.2 Translate to Given-When-Then ACs / 转化为场景化验收条件 (AC)
- Always refine the unstructured story into atomic, verifiable **Given-When-Then** acceptance criteria.
  始终将非结构化的故事提炼为原子化、可验证的 **Given-When-Then（假定-当-则）** 验收条件。
- *Example / 示例*:
  - **Given**: A user is on the login screen and has a valid Google account. / 假定用户处于登录页面且拥有合法的 Google 账户。
  - **When**: The user clicks "Sign in with Google" and successfully authenticates. / 当用户点击“使用 Google 登录”并成功完成鉴权。
  - **Then**: The system logs the user in and redirects them to the home dashboard. / 则系统将登录用户并将其重定向至主控制面板。

### 2.3 Enforce Invariants and Business Boundaries / 明确不变性约束与业务边界
- Do not just define the happy path. The User Scenario must define what happens when business rules are violated:
  不要只定义开心路径。用户场景必须定义违反业务规则时的边界处理：
  - *Data compliance & safety / 合规与数据安全*: What if the third-party account is suspended? / 如果三方账号被封禁了该如何处理？
  - *User Experience budget / 体验底线*: Is there a timeout threshold? Is there a rate-limit threshold for requests? / 是否有超时体验阈值？是否有请求频次限制？

---

## 3. Core Concepts for Beginners / 核心概念快速入门

To ensure a smooth transition to SDS, understand these three core separations:
为确保顺利过渡到 SDS，请理解以下三个核心隔离：

### 3.1 Module vs. Capability (Capability $\neq$ API Interface) / 业务模块与业务能力（能力 $\neq$ 接口）
* **Module** (Business Subdomain): A high-level, stable noun representing a macro business area (e.g., `order`, `billing`, `user_auth`). These are bounded contexts and change very rarely.
  **Module（业务模块）**：一个代表宏观业务领域的、高层级且稳定的名词（如 `order` 订单、`billing` 计费、`user_auth` 用户认证）。这些属于限界上下文，极少发生变更。
* **Capability** (User Feature Scenario): A specific, actionable business transaction or lifecycle inside a Module (e.g., `place_payment_order`, `refund_payment`). These represent actual product requirements and user value.
  **Capability（业务能力）**：业务模块内部一个具体的、可执行的业务交易或生命周期状态机迁移（如 `place_payment_order` 下单支付、`refund_payment` 退款）。这些代表了真实的用户价值和业务场景。
* **The Golden Rule / 黄金法则 (Capability $\neq$ API)**:
  - **A Capability is NOT a physical API interface/endpoint.** A Capability represents business scenarios from the user/product perspective (defined in `spec.md`). A single Capability (like `place_payment_order`) can be physically realized by multiple API endpoints (e.g., separate redirect vs direct-debit endpoints) or polymorphic parameter routes, which are mapped solely in `design.md`. 1-to-1 mapping of APIs to Capabilities is a strict anti-pattern that leads to information duplication and spec fragmentation.
  - **业务能力绝对不能等同于物理 API 接口。** 业务能力是从用户和产品视角定义的业务场景契约（定义在 `spec.md` 中）。同一个业务能力（如“下单支付” `place_payment_order`）在技术实现上可以映射为多个物理网络接口（如单独的“跳转收银台接口”与“直扣接口”），也可以由同一个接口带有多态参数或异步事件来驱动，这些物理映射只应该在 `design.md` 中声明。将“接口”与“能力”进行 1:1 的等同映射是严重的架构反模式，会导致信息重复冗余与真理之源（SOT）的分裂割裂。

### 3.2 `specs/` (Durable) vs. `specs_review/` (Temporary) / 权威区与草稿区
* **`specs_review/`** is the **Drafting Kitchen** (local and gitignored). This is where you conduct research, draft feature proposals, compare technical designs, or record temporary test outputs.
  **`specs_review/`** 是**起草厨房**（本地且被 git 忽略）。这是您进行研究、起草功能提案、对比技术设计或记录临时测试输出的地方。
* **`specs/`** is the **Authoritative Dining Room** (tracked in git). Once a draft/proposal is accepted, promote only the final agreed conclusions into `specs/` as `spec.md` or `design.md`. Source code implementation and automated test suites must only be written to satisfy accepted specifications in `specs/`.
  **`specs/`** 是**权威前厅**（纳入 git 追踪）。一旦草稿或提案被接受，仅将最终达成的结论晋级到 `specs/` 目录下，保存为 `spec.md` 或 `design.md`。源代码实现和自动化测试套件必须纯粹为了满足 `specs/` 中的权威规范而编写。

### 3.3 Where Does the Code Live? / 真实代码写在哪里？
* SDS is a **Sidecar** to your codebase. SDS specification files live *alongside* your source code, not inside it.
  SDS 是您代码库的一个**侧车（Sidecar）**。SDS 规范文件与您的源代码“并排”存放，而不是嵌入在代码内部。
* Your real application code (e.g., Python, Go, TypeScript) lives in standard project folders (like `src/` or `app/`).
  您真实的应用程序代码（如 Python、Go、TypeScript）依然存放在标准的项目文件夹中（如 `src/` 或 `app/`）。
* Automated test suites (e.g., pytest, Jest) live in standard test folders (like `tests/`).
  自动化测试套件（如 pytest、Jest）依然存放在标准的测试文件夹中（如 `tests/`）。
* Implementation code and test cases use `@sds-trace: <capability_id>:AC-n` annotations to trace back to specific Acceptance Criteria (AC) in the specifications.
  实现代码和测试用例使用 `@sds-trace: <capability_id>:AC-n` 注解来追溯到规范中具体的验收条件 (AC)。

---

## 4. Initialize SDS in a Project / 在项目中初始化 SDS

To initialize SDS in a new or existing repository, run the initialization AI Command:
要在新项目或现有代码库中初始化 SDS，请在聊天中向您的 AI 代理发送初始化指令：

```text
/sds init
```

The Agent will automatically handle the setup under the hood (scaffolding directories, creating configs, and templates).
AI 代理将自动在后台处理所有搭建工作（搭建目录、创建配置文件与模板等）。

---

## 5. Classify Documents Properly / 文档正确分类规范

Before writing any markdown file under `specs/` or `specs_review/`, classify it according to its lifecycle stage:
在 `specs/` 或 `specs_review/` 下编写任何 markdown 文件之前，请根据其生命周期阶段对其进行分类：

### 5.1 Transient Workspace / 过程临时空间 (`specs_review/`)
Place any file under `specs_review/<module>/<capability>/` if it represents a decision-in-progress:
如果文件代表正在进行中的决策与讨论，请将其放在 `specs_review/<module>/<capability>/` 下：
- Feasibility assessments, technology comparisons, or audits. / 可行性评估、技术对比或审计报告。
- Refactoring proposals, database migration drafts, or temporary execution plans. / 重构提案、数据库迁移草稿或临时执行计划。
- Verification evidence, run logs, or validation screenshots (under the `verification/` subdirectory). / 验证证据、运行日志或验证截图（存放在 `verification/` 子目录下）。

### 5.2 Global Context / 全局上下文 (`specs/_context/`)
Place files under `specs/_context/` ONLY if they define global, system-wide invariants:
仅在定义全局、系统级不变性约束时，才将文件存放在 `specs/_context/` 下：
- `system-blueprint.md`: Defines global module partitioning, bounded context mappings, and cross-module integration topologies.
  `system-blueprint.md`：定义全局模块划分、限界上下文映射和跨模块集成拓扑图（Context Map）。
- `glossary.md`: The global unified dictionary and business terms representing the macro Ubiquitous Language.
  `glossary.md`：全局统一词汇表和业务术语，代表宏观的统一语言（Ubiquitous Language）。
- `change-history.md`: The macro-level historical change registry.
  `change-history.md`：宏观系统级的历史变更登记册。

### 5.3 Module Context / 模块级上下文 (`specs/<module>/_context/`)
Place files under `specs/<module>/_context/` if they are specific to a single bounded context:
如果文件仅特定于单个限界上下文，请将其存放在 `specs/<module>/_context/` 下：
- `glossary.md`: Module-specific local terminology, terms, and definitions.
  `glossary.md`：模块特定的本地术语、词汇和定义。
- `domain-model.md`: Module-specific local conceptual business entities, aggregate roots, and relationship graphs.
  `domain-model.md`：模块特定的本地概念业务实体、聚合根和关系图。
- `user-journey.md` / `business-flow.md`: Bounded context scenario flows, local invariants, and business rules.
  `user-journey.md` / `business-flow.md`：限界上下文场景流、本地不变性约束和业务规则。
- `change-history.md`: Factual migration timeline and history specific to this module.
  `change-history.md`：该模块特定的历史事实演进线。

### 5.4 Capability Level / 业务能力层级 (`specs/<module>/<capability>/`)
This directory contains exactly two files representing the accepted contract:
该目录仅包含代表已接受契约的两个文件：
- `spec.md`: The 100% Product-Oriented specification (Purpose, Acceptance Criteria, Conceptual Interface Contract, Business Rules).
  `spec.md`：100% 面向产品层面的业务规范（包含目的、验收条件、概念化信息契约、业务规则）。
- `design.md`: The 100% Tech-Oriented design (API physical mappings, local Database Schemas, local Migrations, and local Code Layout).
  `design.md`：100% 面向技术层面的物理实现设计（包含 API 物理映射、本地数据库 Schema、本地迁移和本地代码布局）。

---

## 6. Requirement Delivery Business Flow by Role / 需求到交付的各角色业务流

SDS establishes a clear division of labor and interactive flow among business roles to ensure that specifications remain the Single Source of Truth (SOT):
SDS 建立了清晰的业务角色分工与交互流，确保规范始终是唯一的真理之源 (SOT)：

```text
  [PM / Product Owner]           [Developer / Architect]           [Verifier / QA / AI Agent]
          │                                  │                                  │
    1. Defines "What"                         │                                  │
       (Triggered by User Scenario,           │                                  │
        writes spec.md, glossary.md)          │                                  │
          │ ───[Passes Spec Contract]──────> │                                  │
          │                                  │                                  │
          │                            2. Maps "How"                             │
          │                               (Writes design.md,                     │
          │                                database migrations)                  │
          │                                  │                                  │
          │                            3. Implements Code                        │
          │                               (Adds @sds-trace annotations)          │
          │                                  │ ───[Passes Implementation]──────> │
          │                                  │                                  │
          │                                  │                             4. Verification
          │                                  │                                (Runs project tests,
          │                                  │                                 sds_self_check.py)
          │ <───[Passes Evidence & Green]───────────────────────────────────────│
          │                                                                      │
    5. Requirement Delivered!                                                    │
       (Accepts output)                                                          │
```

### 6.1 Product Manager / Product Owner (PM / PO 角色职责)
- **Primary Ownership**: Defines the **"What"** (Initiated by a **User Scenario**, specifying business rules, boundaries, dictionary, and expectations).
  **核心职责**：定义 **“做什么”（What）** ── 由 **用户场景** 驱动触发，明确业务规则、边界要素、业务词汇表及验收预期。
- **Artifacts Handled**: Writes `specs/_context/glossary.md`, `specs/<module>/_context/user-journey.md`, and `spec.md` (Purpose, Acceptance Criteria, Conceptual Contracts).
  **经手资产**：编写全局/模块级的 `glossary.md`、`user-journey.md`，以及具体能力的 `spec.md`。
- **Rule**: Never write or mandate CamelCase API fields, JSON keys, SQL tables, or deployment variables in the specification. Use plain domain terminology.
  **基本原则**：严禁在 spec.md 中写入驼峰命名的 API、JSON 键、SQL 表或部署变量。必须使用纯粹的业务领域词汇。

### 6.2 Developer / Architect (开发与架构师角色职责)
- **Primary Ownership**: Translates the "What" into the **"How"** (Technical mapping, physical schema, code implementation, and local test coverage).
  **核心职责**：将“做什么”翻译为 **“怎么做”（How）** ── 技术参数映射、物理表结构、代码实现与单元测试覆盖。
- **Artifacts Handled**: Writes `domain-model.md` and `design.md` (Business contract mappings, local schemas, local SQL migration ledger), implements source files under `src/`, and marks code boundaries with `@sds-trace: <capability_id>:AC-n` annotations.
  **经手资产**：编写 `domain-model.md`、`design.md`（包括参数映射表、物理 Schema设计、本地 SQL 账本），编写 `/src` 下的代码，并在关键代码位置标记 `@sds-trace` 注解。
- **Rule**: Keep implementation code strictly focused on satisfying the current accepted specification. Do not build un-spec'd, ad-hoc "future-proof" features.
  **基本原则**：实现代码必须严格契合当前已接受的 spec 规约，严禁自行开发未经 spec 定义的、所谓的“提前扩展”功能。

### 6.3 Verifier / QA / AI Agent (校验者/测试与 AI 代理职责)
- **Primary Ownership**: Verifies that the **"How"** perfectly and provably satisfies the **"What"** defined by the original **User Scenario**.
  **核心职责**：验证 **“怎么做”** 在逻辑与事实上完全满足初始 **用户场景** 所定义的 **“做什么”** 预期。
- **Artifacts Handled**: Runs `python sds_self_check.py` to assert zero spec/code drift, runs full project verification test suites, and records temporary execution run logs or visual snapshots under `specs_review/<module>/<capability>/verification/`.
  **经手资产**：运行本地 `sds_self_check.py` 自检程序保障规范 zero-drift，运行项目测试套件，并在 `specs_review/` 的 `verification/` 目录下记录临时验证证据与日志。
- **Rule**: Only approve requirement delivery once both the SDS structural baseline and custom project validation commands return 100% success.
  **基本原则**：只有当 SDS 结构基线自检和项目自定义校验命令全部返回 100% 成功时，方可批准需求交付。

---

## 7. Development Workflow / 开发工作流

Follow this logical sequence for every requirement change:
每次需求变更请遵循以下 logical 顺序：

```text
  User Scenario Input / Requirement Trigger (用户场景输入 / 需求触发)
                                 ↓
       Draft/Propose in specs_review/ (在 specs_review/ 起草提案)
                                 ↓
   Accept and Promote to specs/ (spec & design) (敲定并晋级到 specs/)
                                 ↓
    Implement Code, Migrations & Tests (编写代码、数据库迁移与测试)
                                 ↓
       Run sds_self_check.py & Verification (运行自检与项目测试验证)
```

### 7.1 Specification Definition First / 规范定义先行
Do not start writing application code until the user or team accepts the specification in `spec.md` and the mapping in `design.md`.
在用户或团队接受 `spec.md` 中的业务规范和 `design.md` 中的技术映射设计之前，不要开始编写应用程序代码。

### 7.2 Test Design Decoupled from Code / 测试设计与实现解耦
Derive automated tests from the acceptance criteria in the spec, not from the physical code structure. Ensure that your automated tests are placed in the project's standard test directories and annotated with `@sds-trace` pointers.
从规约中的验收条件（AC）推导自动化测试用例，而不是根据物理代码结构编写断言。确保您的自动化测试放置在项目的标准测试目录中，并带有 `@sds-trace` 溯源标记。

---

## 8. Configure Verification / 配置项目验证

To enable verification commands in `.sds.harness.yaml`, configure them directly under `verification_commands`. This allows your AI Agent to run them automatically during `/sds verify`:
在 `.sds.harness.yaml` 的 `verification_commands` 下声明校验命令。这将使您的 AI 代理在接收到 `/sds verify` 时，能够全自动运行它们：

```yaml
verification_commands:
  - ["{python}", "-m", "pytest", "tests/"]
  - ["{python}", "-m", "ruff", "check", "app", "tests"]
  - ["npm", "run", "test", "--prefix", "frontend"]
```

---

## 9. New Projects & Requirement Evolution / 全新项目与需求演进

SDS defines clear, actionable stages for bootstrapping a brand new project (0 to 1) and evolving existing business capabilities (1 to N) using standard AI commands:
SDS 通过标准的 AI 交互指令，为初始化全新项目 (0 到 1) 以及演进已有业务能力 (1 到 N) 定义了清晰且可执行的演进阶段：

### 9.1 Phase 1: Bootstrapping a Brand New Project (0 to 1) / 第一阶段：全新项目初始化起步 (0到1)
When starting a project with a clean slate, establish the global boundaries before writing any functional specs:
当从零开始启动一个全新的项目时，在编写任何具体功能规约之前，先确立全局边界：

1. **Run Initialization**: Issue `/sds init` to establish the folder skeletons and configs.
   **执行初始化**：发送 `/sds init` 指令自动建立基础文件夹骨架与配置。
2. **Define Global Context**:
   - Write `specs/_context/system-blueprint.md` to map out the macro modules (e.g., `user_auth`, `payment`) and their communication graph.
   - Write `specs/_context/glossary.md` to define the macro-level common terms of the business.
   **定义全局上下文**：
   - 编写 `specs/_context/system-blueprint.md` 画出系统的宏观业务模块划分和各模块通信拓扑。
   - 编写 `specs/_context/glossary.md` 确定整个系统的全局通用名词定义。
3. **Scaffold First Module Context**: 
   - Create a module directory: `specs/<new_module>/_context/`.
   - Write `glossary.md` for local module-specific terms, and `domain-model.md` to model the conceptual domain entities completely separate from physical SQL tables.
   **建立首个业务模块上下文**：
   - 创建模块目录：`specs/<new_module>/_context/`。
   - 编写该模块专属的本地名词 `glossary.md`，并编写其概念领域模型 `domain-model.md`（完全与 SQL 物理存储表脱耦）。

### 9.2 Phase 2: Creating a New Capability / 第二阶段：全新业务能力的首次创建
When delivering a completely new business capability under an established module:
当在一个已存在的业务模块下，交付一个全新的闭环业务能力时：

1. **Draft in Workspace**: Send `/sds analyze User Scenario: "<description>"` to draft specs in review folder.
   **在草稿区起草**：发送 `/sds analyze User Scenario: "<场景描述>"`，让 AI 在草稿目录下完成方案起草。
2. **Verify Drafts**: Review `spec.md` and `design.md` inside `specs_review/` to ensure perfect conceptual alignment.
   **核对草稿规范**：检查 `specs_review/` 下生成的 `spec.md` 与 `design.md`，确保概念对齐。
3. **Implement**: Send `/sds implement` to promote drafts to `specs/`, write the physical code/migrations, generate standard tests, trace boundaries, and run verifications automatically in the background.
   **一键实现**：发送 `/sds implement` 指令，AI 会自动晋级草稿至 `specs/`、实现物理代码与数据库迁移、生成标准测试、标记 `@sds-trace` 并自动运行后台质量验证。

### 9.3 Phase 3: Evolving an Existing Capability (1 to N) / 第三阶段：已有业务能力的持续演进 (1到N)
**CRITICAL RULE**: Do NOT create a brand new capability folder for incremental changes or feature iterations on an existing capability. Doing so creates information duplication and fractures the Single Source of Truth (SOT). Instead, evolve the capability in place:
**核心红线**：对已有功能进行增量修改、迭代或修补时，**绝对不要创建一个全新命名的业务能力文件夹**！否则会导致信息割裂与 SOT 破裂。必须进行原地演进：

1. **Draft the Evolution Proposal**: Issue `/sds analyze User Scenario: "<evolution description>"` to draft evolution plan under `specs_review/<module>/<existing_capability>/`.
   **起草演进方案**：发送 `/sds analyze User Scenario: "<演进场景描述>"`，AI 会在对应已有能力草稿目录下起草演进方案。
2. **Modify Specs In Place**: The Agent will automatically append new acceptance criteria (e.g., adding `AC-3: User logs in via SMS OTP`) in the existing `spec.md` and update `design.md` with incremental physical mappings/migrations.
   **原地增量修改**：AI 会自动在已有能力的 `spec.md` 中追加新的验收条件（如 `AC-3`），并在 `design.md` 中原地增量修改物理映射与本地物理迁移 SQL。
3. **Implement**: Send `/sds implement`. The Agent will automatically update the source files, implement the feature increment, write standard tests for the new AC, annotate the boundaries with `@sds-trace: <capability_id>:AC-new`, and run validations.
   **一键实现**：发送 `/sds implement`，AI 会自动更新业务代码、实现数据迁移增量、编写对应新 AC 的测试、标记 `@sds-trace` 标签并自动通过质量自检。

---

## 10. Multi-Agent Orchestration & Ecosystem Compatibility / 多智能体协同与生态框架兼容性

To maximize delivery quality and minimize cognitive overhead, SDS is designed to be fully compatible with multi-agent orchestration paradigms and agentic skills frameworks, such as Jesse Vincent's **Superpowers Framework (`obra/superpowers`)**:
为了最大化需求交付质量，同时最小化大模型的认知负荷，SDS 在设计上原生兼容多智能体协同范式及各类智能体技能框架（如 Jesse Vincent 创立的 **Superpowers 智能体框架 (`obra/superpowers`)**）：

When integrated into an active agentic execution host, SDS maps smoothly to standard agentic execution skills:
当集成在活跃的智能体执行宿主中时，SDS 的各项活动可完美映射到标准的智能体执行技能上：

* **Socratic Brainstorming (苏格拉底式头脑风暴)**: The agent applies brainstorming to raw User Scenarios, clarifying business rules and edge cases before writing the first line of specs under `specs_review/`. / 在草稿区动笔前，对原始用户场景进行头脑风暴，明确边界并提炼为 Given-When-Then 验收条件。
* **Defensive Task Planning (防御性微计划)**: The agent breaks down technical mappings in `design.md` into highly modular, bite-sized tasks, each targeting specific file paths with clear local verification checks. / 将 `design.md` 下的物理契约拆解为防御性的微任务计划，精确到具体文件路径与防御性校验步骤。
* **Subagent-Driven Development (SDD / 子智能体驱动开发)**: Spawns fresh, isolated subagents to implement technical code in `src/` and tests in `tests/` without spilling irrelevant parent context. / 针对每个子任务唤醒完全隔离的专职子智能体，干净地生成 `src/` 代码和 `tests/` 测试用例，植入 `@sds-trace`。
* **Verification-Before-Completion (完成前置校验)**: Triggers the project's local `sds_self_check.py` baseline and test suites before declaring a requirement delivered. / 在最终确认完成前，自动运行项目自检脚本和测试，防止任何规范与代码偏离。

---

## 11. Result Description Language / 结果报告描述规范

Always use clear, factual phrasing when reporting results to avoid overclaiming or causing confusion:
在报告结果时，务必使用清晰、符合事实的措辞，以避免过度夸大或引起混淆：

- Use **"SDS baseline passed"** to describe successful validation of directory structures, spec sections, traceability annotations, and drift prevention checks.
  使用 **“SDS baseline passed”（SDS 结构基线通过）** 来描述目录结构、规约必要章节、可追溯性注解和变更漂移防护通过了自检。
- Use **"Project verification passed"** ONLY after all custom-declared test suites, type checking, and compilation commands in `.sds.harness.yaml` return success.
  仅在 `.sds.harness.yaml` 中自定义声明的所有测试套件、类型检查和编译构建命令运行成功后，才使用 **“Project verification passed”（项目验证通过）**。
- Never state "everything is verified" or "ready for production deployment" based purely on local SDS checker success, as runtime environments and cloud release checks are handled by downstream ops pipelines.
  严禁仅凭本地 SDS 检查成功就声称“全部通过”或“可直接发布生产”，因为运行环境和云端发布校验应继续由下游发布流水线保障。
