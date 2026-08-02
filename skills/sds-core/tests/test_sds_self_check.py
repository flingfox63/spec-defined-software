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
            self.assertTrue((root / "sds_self_check.py").is_file())
            agents_path = root / "AGENTS.md"
            self.assertTrue(agents_path.is_file())
            agents_text = agents_path.read_text(encoding="utf-8")
            self.assertIn("do not duplicate specs", agents_text)
            self.assertLessEqual(len(agents_text.splitlines()), 24)


if __name__ == "__main__":
    unittest.main()
