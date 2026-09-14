import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SRC_ROOT = Path(__file__).parent.parent / "src"
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SRC_ROOT))

from sds import __version__
from sds.agent_install import (
    SKILL_BUNDLE_VERSION,
    TARGETS,
    install_agent_integrations,
    resolve_targets,
    build_parser,
    main as install_main,
)
from sds.cli import version_report
from sds.sds_self_check import HARNESS_VERSION


class AgentInstallTests(unittest.TestCase):
    COMMON_TARGETS = ("codex", "opencode", "antigravity", "claude")
    ALL_AGENT_TARGETS = (
        "codex",
        "opencode",
        "claude",
        "cursor",
        "cline",
        "antigravity",
        "gemini",
        "copilot",
        "windsurf",
        "roo",
        "kilo",
    )
    EXPECTED_TARGETS = {
        "shared",
        "codex",
        "opencode",
        "antigravity",
        "claude",
        "cursor",
        "cline",
        "gemini",
        "copilot",
        "windsurf",
        "roo",
        "kilo",
    }

    def make_layout(self, raw):
        root = Path(raw)
        home = root / "home"
        project = root / "project"
        skill_source = root / "skill-source"
        home.mkdir()
        project.mkdir()
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text(
            "---\n"
            "name: sds\n"
            "description: Enforce the Spec-Defined Software workflow.\n"
            "---\n"
            "# SDS\n",
            encoding="utf-8",
        )
        return home, project, skill_source

    def install(
        self,
        home,
        project,
        skill_source,
        *,
        scope="user",
        targets=("codex",),
        command="sds",
        configure_mcp=False,
        force=False,
        dry_run=False,
        opencode_config_version="v1",
    ):
        return install_agent_integrations(
            home=home,
            project_dir=project,
            scope=scope,
            targets=targets,
            command=command,
            configure_mcp=configure_mcp,
            force=force,
            dry_run=dry_run,
            skill_source=skill_source,
            opencode_config_version=opencode_config_version,
        )

    def test_default_detection_and_explicit_subset(self):
        # @sds-trace: agent_integration.install_agents:AC-5
        self.assertEqual(build_parser().parse_args([]).targets, "detected")
        for value in (None, "", [], "  "):
            self.assertEqual(resolve_targets(value, detected_targets=[]), [TARGETS["shared"]])
        for targets, expected in ((None, ("claude", "cline")), ("opencode", ("opencode",))):
            with tempfile.TemporaryDirectory(prefix="sds-default-target-") as raw:
                home, project, source = self.make_layout(raw)
                from sds.agent_install import AgentDetection
                detections = [AgentDetection(TARGETS[name], ("test evidence",)) for name in ("claude", "cline")]
                with mock.patch("sds.agent_install.detect_agent_targets", return_value=detections) as detect:
                    kwargs = {} if targets is None else {"targets": targets}
                    result = install_agent_integrations(home=home, project_dir=project, skill_source=source, **kwargs)
                self.assertTrue(result.ok)
                self.assertEqual(result.selected_targets, expected)
                self.assertEqual(detect.call_count, 1 if targets is None else 0)
                self.assertEqual((home / ".claude/skills/sds/SKILL.md").exists(), targets is None)
                self.assertEqual((home / ".cline/skills/sds/SKILL.md").exists(), targets is None)
                self.assertFalse(any(event.kind == "mcp" for event in result.events))
        with mock.patch("sds.agent_install.install_agent_integrations") as install_call:
            with mock.patch("sds.agent_install._print_summary"), mock.patch("builtins.print"):
                install_main([])
            self.assertEqual(install_call.call_args.kwargs["targets"], "detected")

    def test_mcp_is_opt_in_for_api_and_cli(self):
        # @sds-trace: agent_integration.install_agents:AC-8
        with tempfile.TemporaryDirectory(prefix="sds-opt-in-") as raw:
            home, project, source = self.make_layout(raw)
            existing = project / "opencode.json"
            original = '{"mcp": {"servers": {"sds": null}}}'
            existing.write_text(original)
            result = install_agent_integrations(
                home=home, project_dir=project, skill_source=source,
                scope="project", targets="all",
            )
            self.assertTrue(result.ok)
            self.assertFalse(any(e.kind == "mcp" for e in result.events))
            self.assertEqual(existing.read_text(), original)
            self.assertFalse((project / ".mcp.json").exists())
        parser = build_parser()
        self.assertFalse(parser.parse_args([]).configure_mcp)
        self.assertFalse(parser.parse_args(["--no-mcp"]).configure_mcp)
        self.assertTrue(parser.parse_args(["--with-mcp"]).configure_mcp)
        for argv, expected in (([], False), (["--with-mcp"], True), (["--no-mcp"], False)):
            with mock.patch("sds.agent_install.install_agent_integrations") as install_call:
                with mock.patch("sds.agent_install._print_summary"), mock.patch("builtins.print"):
                    install_main(argv)
                self.assertIs(install_call.call_args.kwargs["configure_mcp"], expected)

    def test_opencode_generations_and_migration_are_idempotent(self):
        # @sds-trace: agent_integration.install_agents:AC-9
        entry = {"type": "local", "command": ["sds", "mcp"]}
        for generation in ("v1", "v2"):
            with self.subTest(generation=generation), tempfile.TemporaryDirectory() as raw:
                home, project, source = self.make_layout(raw)
                path = project / "opencode.json"
                legacy_mcp = {"servers": {"sds": entry}} if generation == "v1" else {"sds": entry}
                original = json.dumps({"mcp": legacy_mcp, "model": "user-choice"})
                path.write_text(original)
                options = dict(scope="project", targets="opencode", configure_mcp=True,
                               opencode_config_version=generation)
                preview = self.install(home, project, source, dry_run=True, **options)
                self.assertTrue(preview.ok)
                self.assertEqual(path.read_text(), original)
                result = self.install(home, project, source, **options)
                self.assertTrue(result.ok)
                expected = {"sds": entry} if generation == "v1" else {"servers": {"sds": entry}}
                self.assertEqual(json.loads(path.read_text()), {"mcp": expected, "model": "user-choice"})
                again = self.install(home, project, source, **options)
                self.assertTrue(again.ok)
                self.assertEqual(again.changed, 0)

    def test_opencode_ambiguous_legacy_layout_is_preserved_even_with_force(self):
        # @sds-trace: agent_integration.install_agents:AC-9
        entry = {"type": "local", "command": ["sds", "mcp"]}
        custom = dict(entry, environment={"PROFILE": "user"})
        cases = [
            ("v1", {"servers": {"sds": custom}}),
            ("v1", {"servers": {"sds": None}}),
            ("v1", {"servers": {"sds": entry, "other": entry}}),
            ("v1", {"sds": entry, "servers": {"sds": entry}}),
            ("v1", {"servers": {"sds": entry}, "timeout": {"startup": 45000}}),
            ("v2", {"timeout": entry}),
            ("v2", {"sds": custom}),
            ("v2", {"other": entry}),
            ("v2", {"servers": {"sds": entry}, "sds": entry}),
        ]
        for generation, mcp in cases:
            with self.subTest(generation=generation, mcp=mcp), tempfile.TemporaryDirectory() as raw:
                home, project, source = self.make_layout(raw)
                path = project / "opencode.json"
                original = json.dumps({"mcp": mcp})
                path.write_text(original)
                result = self.install(home, project, source, scope="project",
                                      targets="opencode", configure_mcp=True, force=True,
                                      opencode_config_version=generation)
                self.assertFalse(result.ok)
                self.assertEqual(path.read_text(), original)

    def test_opencode_v1_preserves_other_servers_and_settings(self):
        # @sds-trace: agent_integration.install_agents:AC-9
        with tempfile.TemporaryDirectory() as raw:
            home, project, source = self.make_layout(raw)
            path = project / "opencode.json"
            other = {"type": "remote", "url": "https://example.test/mcp", "enabled": False}
            path.write_text(json.dumps({"mcp": {"other": other, "servers": other}, "theme": "system"}))
            result = self.install(home, project, source, scope="project",
                                  targets="opencode", configure_mcp=True)
            self.assertTrue(result.ok)
            configured = json.loads(path.read_text())
            self.assertEqual(configured["mcp"]["other"], other)
            self.assertEqual(configured["mcp"]["servers"], other)
            self.assertEqual(configured["mcp"]["sds"], {"type": "local", "command": ["sds", "mcp"]})
            self.assertEqual(configured["theme"], "system")

    def test_common_targets_are_registered_and_agy_alias_is_deduplicated(self):
        self.assertEqual(set(TARGETS), self.EXPECTED_TARGETS)

        agy = resolve_targets("agy")
        self.assertEqual(agy, [TARGETS["antigravity"]])

        resolved = resolve_targets(["agy", "antigravity", "codex", "codex"])
        self.assertEqual(len(resolved), 2)
        self.assertIn(TARGETS["antigravity"], resolved)
        self.assertIn(TARGETS["codex"], resolved)

        detected = resolve_targets(
            "detected", detected_targets=[TARGETS["codex"], TARGETS["codex"]]
        )
        self.assertEqual(detected, [TARGETS["codex"]])

    def test_installs_skills_to_each_user_and_project_location(self):
        # @sds-trace: agent_integration.install_agents:AC-1
        # @sds-trace: agent_integration.install_agents:AC-2
        user_paths = {
            "codex": ".agents/skills/sds/SKILL.md",
            "opencode": ".agents/skills/sds/SKILL.md",
            "claude": ".claude/skills/sds/SKILL.md",
            "cursor": ".agents/skills/sds/SKILL.md",
            "cline": ".cline/skills/sds/SKILL.md",
            "antigravity": ".gemini/config/skills/sds/SKILL.md",
            "gemini": ".agents/skills/sds/SKILL.md",
            "copilot": ".agents/skills/sds/SKILL.md",
            "windsurf": ".agents/skills/sds/SKILL.md",
            "roo": ".agents/skills/sds/SKILL.md",
            "kilo": ".agents/skills/sds/SKILL.md",
        }
        project_paths = {
            "codex": ".agents/skills/sds/SKILL.md",
            "opencode": ".agents/skills/sds/SKILL.md",
            "claude": ".claude/skills/sds/SKILL.md",
            "cursor": ".agents/skills/sds/SKILL.md",
            "cline": ".cline/skills/sds/SKILL.md",
            "antigravity": ".agents/skills/sds/SKILL.md",
            "gemini": ".agents/skills/sds/SKILL.md",
            "copilot": ".agents/skills/sds/SKILL.md",
            "windsurf": ".agents/skills/sds/SKILL.md",
            "roo": ".agents/skills/sds/SKILL.md",
            "kilo": ".agents/skills/sds/SKILL.md",
        }
        user_mcp_paths = {
            "codex": ".codex/config.toml",
            "opencode": ".config/opencode/opencode.json",
            "antigravity": ".gemini/config/mcp_config.json",
            "claude": ".claude.json",
        }
        project_mcp_paths = {
            "codex": ".codex/config.toml",
            "opencode": "opencode.json",
            "antigravity": ".agents/mcp_config.json",
            "claude": ".mcp.json",
        }

        with tempfile.TemporaryDirectory(prefix="sds-agent-paths-") as raw:
            home, project, source = self.make_layout(raw)
            user_result = self.install(
                home,
                project,
                source,
                scope="user",
                targets=self.ALL_AGENT_TARGETS,
                configure_mcp=True,
            )
            project_result = self.install(
                home,
                project,
                source,
                scope="project",
                targets=self.ALL_AGENT_TARGETS,
                configure_mcp=True,
            )

            self.assertFalse(user_result.errors)
            self.assertFalse(project_result.errors)
            for target, relative_path in user_paths.items():
                with self.subTest(scope="user", target=target):
                    installed = home / relative_path
                    self.assertTrue(installed.is_file())
                    self.assertIn("name: sds", installed.read_text(encoding="utf-8"))
            for target, relative_path in project_paths.items():
                with self.subTest(scope="project", target=target):
                    installed = project / relative_path
                    self.assertTrue(installed.is_file())
                    self.assertIn("name: sds", installed.read_text(encoding="utf-8"))
            for target, relative_path in user_mcp_paths.items():
                with self.subTest(scope="user-mcp", target=target):
                    self.assertTrue((home / relative_path).is_file())
            for target, relative_path in project_mcp_paths.items():
                with self.subTest(scope="project-mcp", target=target):
                    self.assertTrue((project / relative_path).is_file())

            user_skill_bundles = list(home.glob("**/skills/sds/SKILL.md"))
            project_skill_bundles = list(project.glob("**/skills/sds/SKILL.md"))
            self.assertEqual(len(user_skill_bundles), 4)
            self.assertEqual(len(project_skill_bundles), 3)
            self.assertEqual(user_result.selection_mode, "explicit")
            self.assertEqual(len(user_result.selected_targets), len(self.ALL_AGENT_TARGETS))

    def test_detected_mode_selects_only_command_detected_targets(self):
        # @sds-trace: agent_integration.install_agents:AC-5
        with tempfile.TemporaryDirectory(prefix="sds-agent-detected-command-") as raw:
            home, project, source = self.make_layout(raw)

            def fake_which(command):
                if command in ("codex", "claude"):
                    return "/tools/{}".format(command)
                return None

            with mock.patch(
                "sds.agent_install.shutil.which", side_effect=fake_which
            ), mock.patch(
                "sds.agent_install._detection_matches", return_value=[]
            ):
                result = self.install(
                    home,
                    project,
                    source,
                    targets="detected",
                    configure_mcp=False,
                )

            self.assertFalse(result.errors)
            self.assertEqual(result.selection_mode, "detected")
            self.assertEqual(result.selected_targets, ("codex", "claude"))
            self.assertTrue((home / ".agents/skills/sds/SKILL.md").is_file())
            self.assertTrue((home / ".claude/skills/sds/SKILL.md").is_file())
            self.assertFalse((home / ".gemini/config/skills/sds").exists())

    def test_detected_mode_recognizes_project_use_marker(self):
        # @sds-trace: agent_integration.install_agents:AC-5
        with tempfile.TemporaryDirectory(prefix="sds-agent-detected-project-") as raw:
            home, project, source = self.make_layout(raw)
            marker = project / ".cursor" / "rules"
            marker.mkdir(parents=True)

            def fake_matches(pattern, _home, _project):
                return [str(marker)] if pattern.endswith("/.cursor/rules") else []

            with mock.patch(
                "sds.agent_install.shutil.which", return_value=None
            ), mock.patch(
                "sds.agent_install._detection_matches", side_effect=fake_matches
            ):
                result = self.install(
                    home,
                    project,
                    source,
                    scope="project",
                    targets="auto",
                    configure_mcp=True,
                )

            self.assertFalse(result.errors)
            self.assertEqual(result.selected_targets, ("cursor",))
            self.assertTrue((project / ".agents/skills/sds/SKILL.md").is_file())
            self.assertTrue((project / ".cursor/mcp.json").is_file())

    def test_detected_mode_without_match_installs_shared_skill_only(self):
        # @sds-trace: agent_integration.install_agents:AC-5
        with tempfile.TemporaryDirectory(prefix="sds-agent-detected-fallback-") as raw:
            home, project, source = self.make_layout(raw)
            with mock.patch(
                "sds.agent_install.shutil.which", return_value=None
            ), mock.patch(
                "sds.agent_install._detection_matches", return_value=[]
            ):
                result = self.install(
                    home,
                    project,
                    source,
                    targets="detected",
                    configure_mcp=True,
                )

            self.assertFalse(result.errors)
            self.assertEqual(result.selected_targets, ("shared",))
            self.assertTrue((home / ".agents/skills/sds/SKILL.md").is_file())
            self.assertEqual(list(project.iterdir()), [])
            self.assertFalse((home / ".codex/config.toml").exists())
            self.assertFalse((home / ".claude.json").exists())

    def test_dry_run_reports_without_writing_any_files(self):
        with tempfile.TemporaryDirectory(prefix="sds-agent-dry-run-") as raw:
            home, project, source = self.make_layout(raw)
            result = self.install(
                home,
                project,
                source,
                scope="project",
                targets=self.COMMON_TARGETS,
                configure_mcp=True,
                dry_run=True,
            )

            self.assertFalse(result.errors)
            self.assertTrue(result.events)
            self.assertEqual(result.changed, 0)
            self.assertGreater(result.planned, 0)
            self.assertEqual(list(home.iterdir()), [])
            self.assertEqual(list(project.iterdir()), [])

    def test_repeated_install_is_idempotent(self):
        with tempfile.TemporaryDirectory(prefix="sds-agent-idempotent-") as raw:
            home, project, source = self.make_layout(raw)
            first = self.install(
                home,
                project,
                source,
                scope="project",
                targets=("agy",),
                configure_mcp=True,
            )
            before = {
                path.relative_to(project): path.read_bytes()
                for path in project.rglob("*")
                if path.is_file()
            }

            second = self.install(
                home,
                project,
                source,
                scope="project",
                targets=("antigravity",),
                configure_mcp=True,
            )
            after = {
                path.relative_to(project): path.read_bytes()
                for path in project.rglob("*")
                if path.is_file()
            }

            self.assertTrue(first.changed)
            self.assertFalse(first.errors)
            self.assertFalse(second.changed)
            self.assertFalse(second.errors)
            self.assertEqual(after, before)

    def test_managed_marker_records_bundle_version_and_upgrades_legacy_marker(self):
        # @sds-trace: agent_integration.install_agents:AC-6
        with tempfile.TemporaryDirectory(prefix="sds-agent-bundle-version-") as raw:
            home, project, source = self.make_layout(raw)
            first = self.install(home, project, source, targets=("codex",))
            marker_path = home / ".agents/skills/sds/.sds-managed.json"
            marker = json.loads(marker_path.read_text(encoding="utf-8"))

            self.assertFalse(first.errors)
            self.assertEqual(marker["bundle_version"], SKILL_BUNDLE_VERSION)
            self.assertEqual(SKILL_BUNDLE_VERSION, __version__)

            marker.pop("bundle_version")
            marker_path.write_text(json.dumps(marker), encoding="utf-8")
            upgraded = self.install(home, project, source, targets=("codex",))
            upgraded_marker = json.loads(marker_path.read_text(encoding="utf-8"))

            self.assertFalse(upgraded.errors)
            self.assertEqual(upgraded.changed, 1)
            self.assertEqual(
                upgraded_marker["bundle_version"], SKILL_BUNDLE_VERSION
            )

    def test_version_report_distinguishes_cli_harness_and_skill_bundle(self):
        # @sds-trace: agent_integration.install_agents:AC-6
        report = version_report().splitlines()

        self.assertEqual(report[0], "sds-cli version {}".format(__version__))
        self.assertEqual(report[1], "SDS harness version {}".format(HARNESS_VERSION))
        self.assertEqual(
            report[2],
            "SDS Skill bundle version {}".format(SKILL_BUNDLE_VERSION),
        )

    def test_release_version_has_one_package_source_and_matches_skill_metadata(self):
        # @sds-trace: agent_integration.install_agents:AC-6
        pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        project_section = pyproject.split("[project]", 1)[1].split("\n[", 1)[0]
        skill = (REPO_ROOT / "skills/sds-core/SKILL.md").read_text(
            encoding="utf-8"
        )
        skill_version = re.search(
            r'(?m)^\s+version:\s*["\']?([^"\'\s]+)', skill
        )

        self.assertIn('dynamic = ["version"]', project_section)
        self.assertNotRegex(project_section, r"(?m)^version\s*=")
        self.assertIn("[tool.hatch.version]", pyproject)
        self.assertIn(
            'path = "skills/sds-core/src/sds/__init__.py"', pyproject
        )
        self.assertIsNotNone(skill_version)
        self.assertEqual(skill_version.group(1), __version__)

    def test_unmanaged_skill_conflict_is_not_overwritten_without_force(self):
        with tempfile.TemporaryDirectory(prefix="sds-agent-conflict-") as raw:
            home, project, source = self.make_layout(raw)
            destination = home / ".agents" / "skills" / "sds" / "SKILL.md"
            destination.parent.mkdir(parents=True)
            destination.write_text("user-owned skill\n", encoding="utf-8")

            result = self.install(home, project, source, targets=("codex",))

            self.assertEqual(destination.read_text(encoding="utf-8"), "user-owned skill\n")
            self.assertFalse(result.changed)

    def test_force_replaces_an_unmanaged_skill_conflict(self):
        with tempfile.TemporaryDirectory(prefix="sds-agent-force-") as raw:
            home, project, source = self.make_layout(raw)
            destination = home / ".agents" / "skills" / "sds" / "SKILL.md"
            destination.parent.mkdir(parents=True)
            destination.write_text("user-owned skill\n", encoding="utf-8")

            result = self.install(
                home,
                project,
                source,
                targets=("codex",),
                force=True,
            )

            self.assertTrue(result.changed)
            self.assertEqual(
                destination.read_text(encoding="utf-8"),
                (source / "SKILL.md").read_text(encoding="utf-8"),
            )

    def test_json_mcp_config_is_merged_without_losing_existing_settings(self):
        with tempfile.TemporaryDirectory(prefix="sds-agent-json-merge-") as raw:
            home, project, source = self.make_layout(raw)
            config_path = project / ".agents" / "mcp_config.json"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "existing": {
                                "command": "existing-server",
                                "args": ["serve"],
                            }
                        },
                        "unrelated": {"preserve": True},
                    }
                ),
                encoding="utf-8",
            )

            result = self.install(
                home,
                project,
                source,
                scope="project",
                targets=("agy",),
                command="custom-sds",
                configure_mcp=True,
            )

            merged = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertFalse(result.errors)
            self.assertEqual(merged["unrelated"], {"preserve": True})
            self.assertEqual(
                merged["mcpServers"]["existing"],
                {"command": "existing-server", "args": ["serve"]},
            )
            self.assertEqual(
                merged["mcpServers"]["sds"],
                {"command": "custom-sds", "args": ["mcp"]},
            )

    def test_invalid_json_mcp_config_is_left_untouched(self):
        with tempfile.TemporaryDirectory(prefix="sds-agent-invalid-json-") as raw:
            home, project, source = self.make_layout(raw)
            config_path = project / ".agents" / "mcp_config.json"
            config_path.parent.mkdir(parents=True)
            invalid_json = '{"mcpServers": '
            config_path.write_text(invalid_json, encoding="utf-8")

            result = self.install(
                home,
                project,
                source,
                scope="project",
                targets=("antigravity",),
                configure_mcp=True,
            )

            self.assertTrue(result.errors)
            self.assertEqual(config_path.read_text(encoding="utf-8"), invalid_json)

    def test_empty_json_mcp_config_is_initialized(self):
        # @sds-trace: agent_integration.install_agents:AC-3
        with tempfile.TemporaryDirectory(prefix="sds-agent-empty-json-") as raw:
            home, project, source = self.make_layout(raw)
            config_path = home / ".gemini" / "config" / "mcp_config.json"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("", encoding="utf-8")

            result = self.install(
                home,
                project,
                source,
                targets=("antigravity",),
                command="custom-sds",
                configure_mcp=True,
            )

            configured = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertFalse(result.errors)
            self.assertEqual(
                configured["mcpServers"]["sds"],
                {"command": "custom-sds", "args": ["mcp"]},
            )

    def test_canonical_json_mcp_command_is_advanced_without_force(self):
        # @sds-trace: agent_integration.install_agents:AC-7
        with tempfile.TemporaryDirectory(prefix="sds-agent-json-upgrade-") as raw:
            home, project, source = self.make_layout(raw)
            config_path = home / ".gemini" / "config" / "mcp_config.json"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "sds": {"command": "/old/bin/sds", "args": ["mcp"]}
                        }
                    }
                ),
                encoding="utf-8",
            )

            result = self.install(
                home,
                project,
                source,
                targets=("antigravity",),
                command="/new/bin/sds",
                configure_mcp=True,
            )

            configured = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertFalse(result.errors)
            self.assertEqual(
                configured["mcpServers"]["sds"],
                {"command": "/new/bin/sds", "args": ["mcp"]},
            )
            self.assertTrue(
                any(
                    event.kind == "mcp"
                    and event.status == "changed"
                    and "advanced canonical" in event.message
                    for event in result.events
                )
            )

    def test_canonical_opencode_mcp_command_is_advanced_without_force(self):
        # @sds-trace: agent_integration.install_agents:AC-7
        with tempfile.TemporaryDirectory(prefix="sds-agent-opencode-upgrade-") as raw:
            home, project, source = self.make_layout(raw)
            config_path = home / ".config" / "opencode" / "opencode.json"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(
                json.dumps(
                    {
                        "mcp": {
                            "servers": {
                                "sds": {
                                    "type": "local",
                                    "command": ["C:\\old\\sds.exe", "mcp"],
                                }
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            result = self.install(
                home,
                project,
                source,
                targets=("opencode",),
                command="C:\\new\\sds.exe",
                configure_mcp=True,
            )

            configured = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertFalse(result.errors)
            self.assertEqual(
                configured["mcp"]["sds"],
                {"type": "local", "command": ["C:\\new\\sds.exe", "mcp"]},
            )

    def test_custom_json_mcp_entry_is_preserved_without_force(self):
        # @sds-trace: agent_integration.install_agents:AC-7
        with tempfile.TemporaryDirectory(prefix="sds-agent-json-custom-") as raw:
            home, project, source = self.make_layout(raw)
            config_path = home / ".gemini" / "config" / "mcp_config.json"
            config_path.parent.mkdir(parents=True)
            custom = {
                "command": "/old/bin/sds",
                "args": ["mcp"],
                "env": {"SDS_PROFILE": "custom"},
            }
            config_path.write_text(
                json.dumps({"mcpServers": {"sds": custom}}),
                encoding="utf-8",
            )

            result = self.install(
                home,
                project,
                source,
                targets=("antigravity",),
                command="/new/bin/sds",
                configure_mcp=True,
            )

            configured = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertFalse(result.errors)
            self.assertEqual(configured["mcpServers"]["sds"], custom)
            self.assertTrue(
                any(
                    event.kind == "mcp" and event.status == "skipped"
                    for event in result.events
                )
            )

    def test_shared_install_removes_only_unchanged_managed_legacy_copy(self):
        # @sds-trace: agent_integration.install_agents:AC-4
        with tempfile.TemporaryDirectory(prefix="sds-agent-retire-legacy-") as raw:
            home, project, source = self.make_layout(raw)
            legacy_root = home / ".gemini" / "skills"

            legacy = self.install(
                home,
                project,
                source,
                targets=("shared",),
            )
            shared_path = home / ".agents" / "skills" / "sds"
            legacy_path = legacy_root / "sds"
            legacy_path.parent.mkdir(parents=True)
            shared_path.rename(legacy_path)
            self.assertFalse(legacy.errors)

            migrated = self.install(
                home,
                project,
                source,
                targets=("gemini",),
            )

            self.assertFalse(migrated.errors)
            self.assertTrue(shared_path.is_dir())
            self.assertFalse(legacy_path.exists())
            self.assertTrue(
                any(
                    event.kind == "cleanup" and event.status == "changed"
                    for event in migrated.events
                )
            )

    def test_shared_install_preserves_modified_managed_legacy_copy(self):
        # @sds-trace: agent_integration.install_agents:AC-4
        with tempfile.TemporaryDirectory(prefix="sds-agent-preserve-legacy-") as raw:
            home, project, source = self.make_layout(raw)
            installed = self.install(
                home,
                project,
                source,
                targets=("shared",),
            )
            shared_path = home / ".agents" / "skills" / "sds"
            legacy_path = home / ".gemini" / "skills" / "sds"
            legacy_path.parent.mkdir(parents=True)
            shared_path.rename(legacy_path)
            (legacy_path / "SKILL.md").write_text(
                "locally modified skill\n", encoding="utf-8"
            )
            self.assertFalse(installed.errors)

            migrated = self.install(
                home,
                project,
                source,
                targets=("gemini",),
            )

            self.assertFalse(migrated.errors)
            self.assertTrue(shared_path.is_dir())
            self.assertTrue(legacy_path.is_dir())
            self.assertTrue(
                any(
                    event.kind == "cleanup" and event.status == "skipped"
                    for event in migrated.events
                )
            )

    def test_windsurf_moves_managed_legacy_copy_to_shared_skill_root(self):
        # @sds-trace: agent_integration.install_agents:AC-1
        # @sds-trace: agent_integration.install_agents:AC-4
        with tempfile.TemporaryDirectory(prefix="sds-agent-windsurf-shared-") as raw:
            home, project, source = self.make_layout(raw)
            installed = self.install(
                home,
                project,
                source,
                targets=("shared",),
            )
            shared_path = home / ".agents" / "skills" / "sds"
            legacy_path = home / ".codeium" / "windsurf" / "skills" / "sds"
            legacy_path.parent.mkdir(parents=True)
            shared_path.rename(legacy_path)
            self.assertFalse(installed.errors)

            migrated = self.install(
                home,
                project,
                source,
                targets=("windsurf",),
            )

            self.assertFalse(migrated.errors)
            self.assertTrue(shared_path.is_dir())
            self.assertFalse(legacy_path.exists())
            self.assertTrue(
                any(
                    event.target == "windsurf"
                    and event.kind == "cleanup"
                    and event.status == "changed"
                    for event in migrated.events
                )
            )

    def test_opencode_mcp_config_uses_v2_schema_and_preserves_other_servers(self):
        with tempfile.TemporaryDirectory(prefix="sds-agent-opencode-json-") as raw:
            home, project, source = self.make_layout(raw)
            config_path = home / ".config" / "opencode" / "opencode.json"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(
                json.dumps(
                    {
                        "theme": "system",
                        "mcp": {
                            "timeout": {"startup": 45000},
                            "servers": {
                                "existing": {
                                    "type": "remote",
                                    "url": "https://example.test/mcp",
                                }
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = self.install(
                home,
                project,
                source,
                targets=("opencode",),
                command="custom-sds",
                configure_mcp=True,
                opencode_config_version="v2",
            )

            merged = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertFalse(result.errors)
            self.assertEqual(merged["mcp"]["timeout"], {"startup": 45000})
            self.assertEqual(merged["theme"], "system")
            self.assertEqual(
                merged["mcp"]["servers"]["existing"],
                {"type": "remote", "url": "https://example.test/mcp"},
            )
            self.assertEqual(
                merged["mcp"]["servers"]["sds"],
                {"type": "local", "command": ["custom-sds", "mcp"]},
            )

    def test_codex_toml_mcp_block_is_appended_once_and_preserves_content(self):
        with tempfile.TemporaryDirectory(prefix="sds-agent-codex-toml-") as raw:
            home, project, source = self.make_layout(raw)
            config_path = home / ".codex" / "config.toml"
            config_path.parent.mkdir(parents=True)
            original = (
                'model = "gpt-5"\n\n'
                "[profiles.review]\n"
                'model = "gpt-5-mini"\n'
            )
            config_path.write_text(original, encoding="utf-8")

            first = self.install(
                home,
                project,
                source,
                targets=("codex",),
                command="custom-sds",
                configure_mcp=True,
            )
            second = self.install(
                home,
                project,
                source,
                targets=("codex",),
                command="custom-sds",
                configure_mcp=True,
            )

            installed = config_path.read_text(encoding="utf-8")
            self.assertFalse(first.errors)
            self.assertFalse(second.errors)
            self.assertTrue(installed.startswith(original))
            self.assertEqual(installed.count("[mcp_servers.sds]"), 1)
            self.assertRegex(
                installed,
                re.compile(
                    r"(?ms)^\[mcp_servers\.sds\]\s*$"
                    r".*?^command\s*=\s*\"custom-sds\"\s*$"
                    r".*?^args\s*=\s*\[\"mcp\"\]\s*$"
                ),
            )
            self.assertFalse(second.changed)


if __name__ == "__main__":
    unittest.main()
