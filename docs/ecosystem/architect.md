# sds-architect (The Tech Design Skill)

The `sds-architect` skill acts as the bridge between the product specification (`spec.md`) and the physical codebase. It is 100% technology-focused.

---

## Key Capabilities

1. **Protocol Selection**: Maps the conceptual contracts defined in `spec.md` to physical communication protocols (REST, GraphQL, gRPC, or events).
2. **Business Contract Mapping**: Synthesizes a explicit translation table converting human-readable concepts from specs into actual physical JSON keys, parameters, or database columns.
3. **Database Schema Design**: Outlines complete table names, column types, foreign keys, indexes, and partition parameters in the `design.md` file.
4. **Data Transition Mapping**: Automatically designs localized database migrations, ensuring backward-compatibility of schemas, and outlines rollback steps.
