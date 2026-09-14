import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HARNESS = Path(__file__).parent.parent / "src" / "sds" / "sds_self_check.py"
SPEC = importlib.util.spec_from_file_location("sds_harness", HARNESS)
SDS_HARNESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SDS_HARNESS)


class SdsSelfCheckTests(unittest.TestCase):
    def make_project(self, root, verification_command):
        root = Path(root)
        (root / "specs" / "_context").mkdir(parents=True)
        (root / "specs" / "demo" / "_context").mkdir(parents=True)
        (root / "specs" / "demo" / "feature").mkdir(parents=True)
        (root / "specs_review").mkdir()
        (root / "specs" / "_context" / "system-blueprint.md").write_text(
            "# System\n",
            encoding="utf-8",
        )
        (root / "specs" / "demo" / "_context" / "user-journey.md").write_text(
            "# Demo journey\n",
            encoding="utf-8",
        )
        (root / "specs" / "demo" / "feature" / "spec.md").write_text(
            "---\n"
            "capability_id: demo.feature\n"
            "ac_derivation:\n"
            "  AC-1:\n"
            "    scenario: ../_context/user-journey.md#demo-journey\n"
            "    reasoning: The actor needs the expected result from the initial state.\n"
            "    ambiguity: none\n"
            "    validation: Valid actions succeed and invalid actions are rejected.\n"
            "side_effects:\n"
            "  database: []\n"
            "  external_apis: []\n"
            "---\n"
            "# Demo\n"
            "## Purpose\nDemo.\n"
            "## Acceptance criteria\n- **AC-1**: Works.\n"
            "## Interface / contract\nNone.\n",
            encoding="utf-8",
        )
        (root / ".sds.harness.yaml").write_text(
            "spec_dir: specs\n"
            "review_dir: specs_review\n"
            "enforce_ac_derivation: true\n"
            "verification_commands:\n"
            f"  - {json.dumps(verification_command)}\n",
            encoding="utf-8",
        )
        return root

    def run_harness(self, root, *arguments):
        return subprocess.run(
            [sys.executable, str(HARNESS), *arguments],
            cwd=root,
            capture_output=True,
            text=True,
        )

    # @sds-trace: specification.validate_contracts:AC-1
    def test_review_reference_notations_and_aliases(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            review = root / "custom_review"
            review.mkdir()
            (review / "note.md").write_text("draft")
            durable = root / "specs" / "spec.md"
            durable.parent.mkdir()
            alias = durable.parent / "alias"
            alias.symlink_to(review, target_is_directory=True)
            forbidden = [
                "[draft](../custom_review/note.md)",
                "[draft]: ../custom_review/note.md", "`custom_review/note.md`",
                r"custom\_review\note.md", "custom%5Freview%2Fnote.md",
                '<a href="../custom_review/note.md">draft</a>',
                "[draft](alias/note.md)", "<alias/note.md>",
            ]
            for value in forbidden:
                with self.subTest(value=value):
                    self.assertTrue(SDS_HARNESS.references_review_artifact(value, durable, review))
            for value in ["The custom_review/ directory is temporary.", "[context](_context/journey.md)", "not_custom_review/note.md"]:
                with self.subTest(value=value):
                    self.assertFalse(SDS_HARNESS.references_review_artifact(value, durable, review))

    def test_review_references_are_rejected_in_all_durable_document_roles(self):
        for relative in ["specs/demo/feature/spec.md", "specs/demo/feature/design.md", "specs/demo/_context/user-journey.md"]:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as raw:
                root = self.make_project(raw, [])
                path = root / relative
                with path.open("a") as handle:
                    handle.write("\n[draft]: ../../../specs_review/decision.md\n")
                result = self.run_harness(root)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                diagnostics = json.loads((root / "specs_review/diagnostics.json").read_text())
                self.assertIn("DURABLE_DOC_LINKS_EPHEMERAL_ARTIFACT", [e["code"] for e in diagnostics["errors"]])

    # @sds-trace: specification.validate_contracts:AC-2
    def test_derivation_requires_every_ac_and_resolved_context(self):
        with tempfile.TemporaryDirectory() as raw:
            root = self.make_project(raw, [])
            spec = root / "specs/demo/feature/spec.md"
            fm, body = SDS_HARNESS.parse_spec_file(spec)
            validate = lambda data, acs={"AC-1"}: SDS_HARNESS.validate_ac_derivation(spec, root / "specs", data, acs)
            self.assertEqual(validate(fm), [])
            self.assertFalse(SDS_HARNESS.is_unresolved("Reject unresolved interpretations and preserve placeholder files."))
            self.assertTrue(validate(fm, {"AC-1", "AC-2"}))
            self.assertTrue(validate(fm, set()))
            for field, value in [
                ("reasoning", ""), ("ambiguity", "pending"), ("validation", "<expected>"),
                ("scenario", "../_context/missing.md"),
                ("scenario", "../_context/user-journey.md#missing"),
                ("scenario", "../../../specs_review/note.md"),
                ("scenario", "https://example.com/context.md"),
                ("validation", []),
                ("scenario", "http://[invalid"),
            ]:
                data = json.loads(json.dumps(fm))
                data["ac_derivation"]["AC-1"][field] = value
                with self.subTest(field=field, value=value):
                    self.assertTrue(validate(data))

    def test_missing_derivation_fails_default_end_to_end_gate(self):
        with tempfile.TemporaryDirectory() as raw:
            root = self.make_project(raw, [])
            spec = root / "specs/demo/feature/spec.md"
            spec.write_text(spec.read_text().replace("ac_derivation:", "old_derivation:"))
            result = self.run_harness(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            diagnostics = json.loads((root / "specs_review/diagnostics.json").read_text())
            self.assertIn("INVALID_AC_DERIVATION", [e["code"] for e in diagnostics["errors"]])

    # @sds-trace: specification.validate_contracts:AC-3
    def test_initializer_and_packaged_authoring_templates_stay_aligned(self):
        templates = HARNESS.parents[2] / "templates"
        self.assertEqual(SDS_HARNESS.DEFAULT_SPEC_TEMPLATE,
                         (templates / "spec.template.md").read_text().replace("<module>.", "<module_name>."))
        self.assertEqual(SDS_HARNESS.DEFAULT_DESIGN_TEMPLATE,
                         (templates / "design.template.md").read_text())
        with tempfile.TemporaryDirectory() as raw:
            self.assertEqual(self.run_harness(Path(raw), "--init").returncode, 0)
            spec = Path(raw) / "specs/example_module/example_capability/spec.md"
            fm, body = SDS_HARNESS.parse_spec_file(spec)
            self.assertEqual(set(fm["ac_derivation"]), SDS_HARNESS.extract_ac_ids(body))
            self.assertTrue(SDS_HARNESS.load_config(Path(raw))["enforce_ac_derivation"])

    # @sds-trace: specification.validate_contracts:AC-1
    def test_nested_review_directory_uses_full_path(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            review = root / "docs/review"
            durable = root / "specs/demo/spec.md"
            for text, expected in (("review/x.md", False), ("docs/review/x.md", True),
                                   ("`docs/review/x.md`", True), ("```\ndocs/review/x.md\n```", True),
                                   ("[draft](../../docs/review/x.md)", True)):
                self.assertEqual(SDS_HARNESS.references_review_artifact(text, durable, review, root), expected, text)

    # @sds-trace: specification.validate_contracts:AC-2
    def test_business_comparisons_are_not_placeholders(self):
        for text in ("Rejects orders when total < 100 or quantity > 5", "Applies when latency < 200ms"):
            self.assertFalse(SDS_HARNESS.is_unresolved(text))
        for text in ("<expected>", "  <Explain outcome>  ", "TODO decide"):
            self.assertTrue(SDS_HARNESS.is_unresolved(text))

    # @sds-trace: specification.validate_contracts:AC-2
    def test_upgrade_policy_matrix_and_single_warning(self):
        for policy in (None, False, True):
            for records in ("complete", "missing", "partial"):
                with self.subTest(policy=policy, records=records), tempfile.TemporaryDirectory() as raw:
                    root = self.make_project(raw, [])
                    config = root / ".sds.harness.yaml"
                    text = config.read_text().replace("enforce_ac_derivation: true\n", "").replace("verification_commands:\n  - []", "verification_commands: []")
                    if policy is not None:
                        text += "enforce_ac_derivation: " + str(policy).lower() + "\n"
                    config.write_text(text)
                    spec = root / "specs/demo/feature/spec.md"
                    text = spec.read_text()
                    if records == "missing":
                        text = text.replace("ac_derivation:", "old_derivation:")
                    elif records == "partial":
                        text += "\n- **AC-2**: Another outcome.\n"
                    spec.write_text(text)
                    second = root / "specs/demo/second/spec.md"
                    second.parent.mkdir()
                    second.write_text(text.replace("demo.feature", "demo.second"))
                    result = self.run_harness(root)
                    fails = policy is True and records != "complete"
                    self.assertEqual(result.returncode, int(fails), result.stdout + result.stderr)
                    if fails:
                        diagnostics = json.loads((root / "specs_review/diagnostics.json").read_text())
                        self.assertIn("INVALID_AC_DERIVATION", [e["code"] for e in diagnostics["errors"]])
                    elif policy is None:
                        self.assertEqual(result.stdout.count("AC derivation compatibility mode:"), 1)
                    elif policy is False:
                        self.assertEqual(result.stdout.count("AC scenario derivation check explicitly disabled"), 1)

    def test_parses_verification_argv_arrays(self):
        config = SDS_HARNESS.parse_simple_yaml(
            'verification_commands:\n  - ["python", "-m", "pytest"]\n'
        )
        self.assertEqual(
            config["verification_commands"],
            [["python", "-m", "pytest"]],
        )

    def test_drift_guard_covers_runtime_build_migration_and_release_files(self):
        guarded = [
            "frontend.tsx",
            "schema.sql",
            "deploy.sh",
            "auth-service.service",
            "pyproject.toml",
            "package.json",
            "Dockerfile",
        ]
        for filename in guarded:
            with self.subTest(filename=filename):
                self.assertTrue(SDS_HARNESS.is_drift_guarded_path(Path(filename)))

    def test_runs_project_verification_command(self):
        with tempfile.TemporaryDirectory(prefix="sds-verification-") as raw:
            root = self.make_project(
                raw,
                ["{python}", "-c", "raise SystemExit(0)"],
            )
            result = self.run_harness(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Configured project verification #1 passed", result.stdout)

    def test_reports_failed_project_verification(self):
        with tempfile.TemporaryDirectory(prefix="sds-verification-fail-") as raw:
            root = self.make_project(
                raw,
                ["{python}", "-c", "raise SystemExit(7)"],
            )
            result = self.run_harness(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            diagnostics = json.loads(
                (root / "specs_review" / "diagnostics.json").read_text(encoding="utf-8")
            )
            self.assertTrue(
                any(
                    item["code"] == "PROJECT_VERIFICATION_FAILED"
                    for item in diagnostics["errors"]
                )
            )

    def test_rejects_durable_link_to_ephemeral_artifact(self):
        with tempfile.TemporaryDirectory(prefix="sds-review-link-") as raw:
            root = self.make_project(
                raw,
                ["{python}", "-c", "raise SystemExit(0)"],
            )
            spec_path = root / "specs" / "demo" / "feature" / "spec.md"
            spec_path.write_text(
                spec_path.read_text(encoding="utf-8")
                + "\n[review](../../../specs_review/assessment.md)\n",
                encoding="utf-8",
            )
            result = self.run_harness(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            diagnostics = json.loads(
                (root / "specs_review" / "diagnostics.json").read_text(encoding="utf-8")
            )
            self.assertTrue(
                any(
                    item["code"] == "DURABLE_DOC_LINKS_EPHEMERAL_ARTIFACT"
                    for item in diagnostics["errors"]
                )
            )

    def test_rejects_module_without_context(self):
        with tempfile.TemporaryDirectory(prefix="sds-module-context-") as raw:
            root = self.make_project(
                raw,
                ["{python}", "-c", "raise SystemExit(0)"],
            )
            context_path = root / "specs" / "demo" / "_context" / "user-journey.md"
            context_path.unlink()
            result = self.run_harness(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            diagnostics = json.loads(
                (root / "specs_review" / "diagnostics.json").read_text(encoding="utf-8")
            )
            self.assertTrue(
                any(item["code"] == "MISSING_MODULE_CONTEXT" for item in diagnostics["errors"])
            )

    def test_rejects_capability_id_that_disagrees_with_path(self):
        with tempfile.TemporaryDirectory(prefix="sds-capability-path-") as raw:
            root = self.make_project(
                raw,
                ["{python}", "-c", "raise SystemExit(0)"],
            )
            spec_path = root / "specs" / "demo" / "feature" / "spec.md"
            spec_path.write_text(
                spec_path.read_text(encoding="utf-8").replace(
                    "capability_id: demo.feature",
                    "capability_id: ledger.feature",
                ),
                encoding="utf-8",
            )
            result = self.run_harness(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            diagnostics = json.loads(
                (root / "specs_review" / "diagnostics.json").read_text(encoding="utf-8")
            )
            self.assertTrue(
                any(item["code"] == "CAPABILITY_PATH_MISMATCH" for item in diagnostics["errors"])
            )

    def test_init_scaffolds_parseable_empty_verification_gate(self):
        with tempfile.TemporaryDirectory(prefix="sds-init-") as raw:
            root = Path(raw)
            result = self.run_harness(root, "--init")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            config = SDS_HARNESS.load_config(root)
            self.assertEqual(config["verification_commands"], [])
            checked = self.run_harness(root)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertFalse((root / "sds_self_check.py").exists())
            agents_path = root / "AGENTS.md"
            self.assertTrue(agents_path.is_file())
            agents_text = agents_path.read_text(encoding="utf-8")
            self.assertIn("do not duplicate specs", agents_text)
            self.assertLessEqual(len(agents_text.splitlines()), 24)


if __name__ == "__main__":
    unittest.main()
