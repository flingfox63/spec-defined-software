# sds-architect (The Tech Design Skill)

The `sds-architect` skill acts as the bridge between the product specification (`spec.md`) and the physical codebase. It is 100% technology-focused.

> [!NOTE]
> **Ecosystem Status: 🟡 In Progress / 模块开发状态：进行中**
> This module (`sds-architect`) is currently **In Progress** as outlined in our [Roadmap](../index.md#ecosystem-roadmap). The specifications and instructions below describe the target design and behavioral interface, but the physical skill package is not yet fully active.
> 本模块目前处于**开发中**阶段。下述规范和指令描述了其目标架构和行为定义，但其实体技能包尚未正式激活。

---

## Key Capabilities

1. **Protocol Selection**: Maps the conceptual contracts defined in `spec.md` to physical communication protocols (REST, GraphQL, gRPC, or events).
2. **Business Contract Mapping**: Synthesizes a explicit translation table converting human-readable concepts from specs into actual physical JSON keys, parameters, or database columns.
3. **Database Schema Design**: Outlines complete table names, column types, foreign keys, indexes, and partition parameters in the `design.md` file.
4. **Data Transition Mapping**: Automatically designs localized database migrations, ensuring backward-compatibility of schemas, and outlines rollback steps.

Map every AC to a technical mechanism, positive test and boundary/counterexample test. Preserve the business outcome chosen from context/spec; resolve contradictions there before implementation. Mark inapplicable technical sections with a reason instead of inventing APIs or tables.
