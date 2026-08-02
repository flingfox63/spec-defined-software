# sds-ops (The Release Skill)

`sds-ops` (evolved from `ec2-deploy`) ensures that our high software standards are maintained all the way into production. It focuses on atomic deployment, zero-downtime, and automatic rollback on failure.

---

## Key Capabilities

1. **Capistrano-Style Atomic Releases**: Packages the verified software into dated release subdirectories and uses symbolic links (`symlinks`) to activate the active production version instantly.
2. **Safe Migration Execution**: Executes database migration steps in a strict, pre-defined order before activating the active code directory, verifying backward compatibility.
3. **Automated Smoke Testing**: Runs post-release verification checks against the live environment.
4. **Instant Rollback**: If any post-deployment smoke test, health check, or local invariant is violated, the system instantly reverts the symlink to the previous stable release directory, minimizing downtime and maintaining data integrity.
