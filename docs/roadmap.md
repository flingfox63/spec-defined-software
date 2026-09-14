# Validation roadmap

The following evaluation work is planned for a later release. It is not an
implemented gate or evidence that Skill behavior has already been measured.

## Behavior evaluation across Skill releases

Use a fixed scenario set covering ambiguous requirements, business constraints,
technical details placed in specs, temporary document references, authorization,
and retries. Run the same prompt and initial context with the old and candidate
Skill in isolated workspaces. Pin model and runtime settings and repeat trials;
store the input, output, release identity and evaluation rubric. A fixed random
seed alone is not a reproducibility guarantee for hosted models.

Score each AC for a valid scenario source, reasoning consistent with the actor's
goal and boundaries, explicit treatment of competing interpretations, and a
positive and negative verification case. Score spec/design separation by meaning:
a user-required protocol or performance promise can belong in a spec, so a
zero-technical-word counter is not a valid acceptance gate. Review failures
without showing the evaluator which release produced the result. Report per-case
regressions and repeated-run variability before choosing pass thresholds.

## Skill, documentation and checker consistency

Maintain a rule inventory mapping each requirement to its authoritative text,
configuration key and finding code when mechanically enforceable. Mark semantic
rules as human/agent-reviewed rather than inventing finding codes for them.
Evaluate behavior against shared fixtures instead of asserting identical wording
across every document. Include skipped-policy behavior and migration guidance.

## Reusable negative fixtures and release matrix

Promote focused temporary test inputs into a reusable fixture corpus outside
`specs/`. Each fixture declares expected exit status and specific findings.
Cover escaped and aliased references, nested review directories, contradictory
scenarios, malformed derivation records and misleading technical specifications.
Keep passing examples separate from deliberately invalid fixtures.

Already covered in 1.2.2 regression tests: missing/partial/complete derivations
with absent/false/true policies, fresh init followed by check, and detected versus
explicit installation targets. Later release checks should run the same matrix
against built packages and prior supported releases in isolated homes, including
both bootstrap platforms. Inspect expected file effects and preservation of
unselected agents' configuration, rather than relying on textual snapshots.

## Exit criteria for the evaluation work

Publish a reproducible runner, versioned scenario corpus, documented rubric and
reviewed baseline results. Add a release gate only after measuring false positives
and outcome variability. Until then, structural checks and separate scenario
review remain complementary, limited evidence.
