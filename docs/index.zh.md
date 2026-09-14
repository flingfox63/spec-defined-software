# SDS — 规格定义软件 (需求交付版本)

欢迎来到软件工程的未来。

**规格说明定义软件 (Spec-Defined Software, SDS)** 代表了软件交付模式的重大变革：从传统的“手动编码”升级为精准的、AI 协同的**“规格定义”**。在这一范式中，业务需求的完整行为和业务标识被元数据化写入 `spec.md`（定义“做什么”），并映射到 `design.md` 的技术设计上（定义“怎么做”）。

实际的物理代码、数据库迁移、测试套件和部署配置被视为逻辑衍生品，它们完全可以由先进 of AI 引擎自动合成、验证与自我修复。

---

## 🚀 SDS 核心理念：代码即编译产物

始终将**规格说明书（Specification）**视为整个需求交付流程的绝对唯一真理源。优先保证规格说明的完整性与清晰度，而非急于直接编码。

```text
  [ 用户场景 ] ➔ [ 达成共识的规约与设计 ] ➔ [ 物理实现 ] ➔ [ 自动化验证 ] ➔ [ 需求交付 ]
```

代码仅仅是已交付需求的一个编译产物。通过将修改聚焦在“规格说明优先”的交付模型上，我们的每一次改动都能百分之百地追溯回规格说明书中的验收准则（AC），从而实现“零漂移（Zero-Drift）”式高质量开发。

---

## 🛠️ SDS 多技能生命周期工具链

目前已发布的 `sds-core` Skill 提供规格校验、可追溯性检查、Git Hook
和 MCP 接入。以下专用生命周期 Skill 描述的是产品路线图；是否可用以
下方路线图表格中的状态为准：

1. **`sds-ideator`（需求阶段，进行中）**：计划提供苏格拉底式流程，将模糊诉求提炼为 Gherkin 风格的验收准则（AC）。
2. **`sds-architect`（设计阶段，进行中）**：计划将已确认的产品规格转换为技术契约和 `design.md`。
3. **`sds-coder`（实现阶段，规划中）**：计划辅助代码实现并维护 `@sds-trace` 覆盖。
4. **`sds-qa`（验证阶段，规划中）**：计划提供 AC 驱动的测试合成与质量闸门。
5. **`sds-ops`（交付阶段，规划中）**：计划提供原子化部署与回滚流程。

---

## 📦 极速上手

只需几秒，即可在本地和 AI 环境中运行 SDS 命令行工具：

### 1. 一键安装
使用我们的一键脚本安装 CLI 工具：
```bash
curl -fsSL https://raw.githubusercontent.com/flingfox63/spec-defined-software/main/install.sh | sh
```

### 2. 安装到 AI Agent 与常用 IDE

默认检测本地 Agent 并安装已发布的 SDS Agent Skill，
默认不修改 MCP 配置：

```bash
sds install-agents
```

默认采用用户级安装并自动检测；没有检测结果时仅安装共享 Skill。
使用 `--targets opencode,claude` 选择要安装或升级的 Agent，
也可以安装所有目标，或只安装到某个项目：

```bash
sds install-agents --targets all
sds install-agents --targets codex,opencode,claude,agy
sds install-agents --targets cursor --scope project --project-dir /path/to/repo
```

支持的选择器包括 `shared`、`codex`、`opencode`、`claude`、`cursor`、`cline`、
`antigravity`（别名 `agy`）、`gemini`、`copilot`（别名 `vscode`）、
`windsurf`、`roo` 和 `kilo`。SDS 遵循 Agent Skills 目录标准；安装过程
可幂等重复执行：支持 `.agents/skills` 的 Agent 共用一份 SDS Skill，只有
必须使用专属发现目录的客户端才会获得独立副本。托管标记会记录 Skill
包版本和内容哈希，旧版本会原位更新而不会产生重复副本。已有的非 SDS
Skill、MCP 服务及其他配置都会保留。需要 MCP 时显式使用 `--with-mcp`；
`--no-mcp` 保留为默认行为的兼容别名。使用
`--dry-run` 可预览变更；`sds version` 会分别显示 CLI、校验 Harness 和 Skill
包版本。

### 3. 初始化项目
在业务仓库根目录下执行骨架初始化：
```bash
sds init
```
这将生成配置文件 `.sds.harness.yaml` 并建立标准的 `specs/` 目录规范。

### 4. 执行规范校验
对代码层注释、规格说明格式以及需求一致性进行全方位扫描：
```bash
sds check
```

每个 AC 都需要场景推导记录：持久上下文来源、推导理由、歧义取舍和正例／反例预期。
新项目显式启用推导检查；旧项目缺少配置键时只提示一次迁移警告，补齐记录后设置 `enforce_ac_derivation: true` 启用。spec 描述业务结果，design 逐项承接
技术机制和测试；结构完整不代表语义正确，仍需对照上下文独立审阅。持久文档禁止以
任何引用方式依赖临时评审文件。详见[工作流](workflow.md)和[模板](reference/templates.md)。

### 可选的手动 MCP 配置与故障排查

需要 MCP 时执行 `sds install-agents --with-mcp --targets TARGET`。
如果客户端找不到 CLI，追加 `--command /absolute/path/to/sds`。
OpenCode 默认使用 v1 配置；v2 客户端需追加 `--opencode-config-version v2`。
旧版 SDS 写入的标准嵌套配置会在显式安装 MCP 时安全迁移；自定义或混合配置
保持原样并报错提示人工处理。手动配置 stdio MCP 时，命令为 `sds`，参数为
`["mcp"]`。

## 🗺️ 生态路线图 (Ecosystem Roadmap)

SDS 正在从一个基础的静态校验工具，逐步演进为一个端到端、完全自动化的 AI 协同软件交付操作系统。以下是我们的核心里程碑与发展时间线：

| 阶段 / 模块 | 计划时间 | 当前状态 | 核心交付物与能力介绍 |
| :--- | :--- | :--- | :--- |
| **`sds-core`**<br>*(校验护栏)* | 已发布 | **🟢 已发布** | • 静态校验 `specs/` 目录结构与 Frontmatter 状态。<br>• 物理集成 Pre-commit 钩子与跨平台一键安装器。<br>• 暴露标准的 Model Context Protocol (MCP) 语义服务器。 |
| **`sds-ideator`**<br>*(苏格拉底产品经理)* | 2026 Q3 | **🟡 进行中** | • 苏格拉底式对齐 Prompt 套件，将模糊想法提炼为 BDD Gherkin AC。<br>• 自动在 `specs_review/` 目录下合成并起草初始 `spec.md` 规范。 |
| **`sds-architect`**<br>*(架构总监)* | 2026 Q3 | **🟡 进行中** | • 将通过的业务规范一键编译为具象的技术实现方案。<br>• 自动生成 TypeScript/Go API 契约、数据库迁移脚本并写入 `design.md`。 |
| **`sds-coder`**<br>*(自主代码合成)* | 2026 Q4 | **🔵 规划中** | • 智能体驱动的自动化编码器，直接基于 Spec 生成业务代码。<br>• 自动插桩 `@sds-trace` 并自动修复测试编译/规范漂移报错。 |
| **`sds-qa`**<br>*(BDD 测试编译器)* | 2026 Q4 | **🔵 规划中** | • 将 AC 自动编译为可运行的集成测试、单元测试与 E2E 校验脚本。<br>• 强制执行质量卡点检验，通过后才可解锁后续部署管道。 |
| **`sds-ops`**<br>*(原子化无损发布)* | 2027 Q1 | **🔵 规划中** | • 类似 Capistrano 风格的原子化符号链接（Symlink）版本切换发布。<br>• 自动隔离 Virtualenv 并支持一键免密无损回滚策略。 |

## 💖 致敬与灵感来源 (Heritage & Inspiration)

Spec-Defined Software (SDS) 非常荣幸继承了开源社区的优秀传统，本项目的核心设计深受 GitHub 先驱项目 [spec-kit](https://github.com/github/spec-kit) 规范开发模式的启发并由其演进而来。 

我们在其经典 `spec-kit` 规范驱动理念之上，针对 AI 原生开发时代进行了大幅度的能力扩展 —— 物理引入了零偏差静态校验器、多智能体协同安全网、以及物理层双向可追溯 `@sds-trace` 机制，致力于打造 AI 原生时代下坚不可摧的需求契约闭环。

---

> [!NOTE]
> 已发布的 `sds-core` Skill 可接入上方列出的 Agent Skills 与 MCP 环境。
> 标为“进行中”或“规划中”的生命周期 Skill 会在正式发布后才进入安装包。

后续行为评估、规则一致性与反例集计划见 [Validation roadmap](roadmap.md)。
