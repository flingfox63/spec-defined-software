"""Install the SDS Agent Skill and MCP server across supported coding agents.

The installer deliberately uses only the Python standard library.  It treats
existing, user-owned skills and MCP entries as immutable unless ``--force`` is
explicitly supplied, and it updates SDS-managed skill copies atomically.
"""

from __future__ import print_function

import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple, Union

from sds import __version__


SKILL_NAME = "sds"
SKILL_BUNDLE_VERSION = __version__
MANAGED_MARKER = ".sds-managed.json"
TOML_BLOCK_START = "# >>> sds-cli managed MCP server >>>"
TOML_BLOCK_END = "# <<< sds-cli managed MCP server <<<"
DETECTED_TARGET_NAMES = ("detected", "auto")

EDITOR_EXTENSION_ROOTS = (
    "{home}/.vscode/extensions",
    "{home}/.cursor/extensions",
    "{home}/.windsurf/extensions",
)


def _extension_detection_globs(*extension_ids: str) -> Tuple[str, ...]:
    return tuple(
        "{}/{}*".format(root, extension_id)
        for root in EDITOR_EXTENSION_ROOTS
        for extension_id in extension_ids
    )


@dataclass(frozen=True)
class AgentTarget:
    """Filesystem conventions for one supported agent or IDE."""

    name: str
    aliases: Tuple[str, ...]
    user_skill_root: Path
    project_skill_root: Path
    user_mcp_path: Optional[Path] = None
    project_mcp_path: Optional[Path] = None
    mcp_style: Optional[str] = None
    description: str = ""
    retired_user_skill_roots: Tuple[Path, ...] = ()
    retired_project_skill_roots: Tuple[Path, ...] = ()
    detection_commands: Tuple[str, ...] = ()
    detection_globs: Tuple[str, ...] = ()
    project_detection_globs: Tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentDetection:
    """One detected target plus the local evidence used to select it."""

    target: AgentTarget
    evidence: Tuple[str, ...]


@dataclass(frozen=True)
class InstallEvent:
    target: str
    kind: str
    path: Path
    status: str
    message: str


@dataclass
class InstallSummary:
    events: List[InstallEvent] = field(default_factory=list)
    selection_mode: str = "explicit"
    selected_targets: Tuple[str, ...] = ()
    detections: List[AgentDetection] = field(default_factory=list)

    @property
    def changed(self) -> int:
        return sum(event.status == "changed" for event in self.events)

    @property
    def planned(self) -> int:
        return sum(event.status == "planned" for event in self.events)

    @property
    def unchanged(self) -> int:
        return sum(event.status == "unchanged" for event in self.events)

    @property
    def skipped(self) -> int:
        return sum(event.status == "skipped" for event in self.events)

    @property
    def errors(self) -> List[InstallEvent]:
        return [event for event in self.events if event.status == "error"]

    @property
    def ok(self) -> bool:
        return not self.errors


# Prefer the cross-agent .agents/skills discovery path whenever a target
# supports it at the selected scope. This keeps one managed skill bundle while
# MCP registrations remain target-specific.
# @sds-trace: agent_integration.install_agents:AC-1
# @sds-trace: agent_integration.install_agents:AC-2
TARGETS = {
    "shared": AgentTarget(
        "shared",
        ("agents", "agent-skills"),
        Path(".agents/skills"),
        Path(".agents/skills"),
        description="Open Agent Skills shared discovery path",
    ),
    "codex": AgentTarget(
        "codex",
        ("openai-codex",),
        Path(".agents/skills"),
        Path(".agents/skills"),
        Path(".codex/config.toml"),
        Path(".codex/config.toml"),
        "codex-toml",
        "OpenAI Codex CLI, desktop app, and IDE extension",
        detection_commands=("codex",),
        detection_globs=(
            "/Applications/Codex.app",
            "{home}/Applications/Codex.app",
            "{home}/AppData/Local/Programs/Codex/Codex.exe",
        ),
        project_detection_globs=("{project}/.codex/environments",),
    ),
    "opencode": AgentTarget(
        "opencode",
        ("open-code",),
        Path(".agents/skills"),
        Path(".agents/skills"),
        Path(".config/opencode/opencode.json"),
        Path("opencode.json"),
        "opencode-json",
        "OpenCode CLI and IDE",
        (Path(".config/opencode/skills"),),
        (Path(".opencode/skills"),),
        detection_commands=("opencode",),
        project_detection_globs=(
            "{project}/.opencode/agents",
            "{project}/.opencode/commands",
        ),
    ),
    "claude": AgentTarget(
        "claude",
        ("claude-code", "anthropic"),
        Path(".claude/skills"),
        Path(".claude/skills"),
        Path(".claude.json"),
        Path(".mcp.json"),
        "mcp-json",
        "Claude Code CLI and IDE integrations",
        detection_commands=("claude",),
        project_detection_globs=(
            "{project}/CLAUDE.md",
            "{project}/.claude/settings.json",
            "{project}/.claude/commands",
        ),
    ),
    "cursor": AgentTarget(
        "cursor",
        ("cursor-ide",),
        Path(".agents/skills"),
        Path(".agents/skills"),
        Path(".cursor/mcp.json"),
        Path(".cursor/mcp.json"),
        "mcp-json",
        "Cursor editor and cursor-agent CLI",
        (Path(".cursor/skills"),),
        (Path(".cursor/skills"),),
        detection_commands=("cursor", "cursor-agent"),
        detection_globs=(
            "/Applications/Cursor.app",
            "{home}/Applications/Cursor.app",
            "{home}/AppData/Local/Programs/cursor/Cursor.exe",
        ),
        project_detection_globs=(
            "{project}/.cursor/rules",
            "{project}/.cursor/hooks.json",
        ),
    ),
    "cline": AgentTarget(
        "cline",
        ("cline-vscode",),
        Path(".cline/skills"),
        Path(".cline/skills"),
        description="Cline for VS Code and JetBrains",
        detection_commands=("cline",),
        detection_globs=_extension_detection_globs(
            "saoudrizwan.claude-dev-", "cline.cline-"
        ),
        project_detection_globs=(
            "{project}/.clinerules",
            "{project}/.cline/rules",
        ),
    ),
    "antigravity": AgentTarget(
        "antigravity",
        ("agy", "antigravity-cli", "google-antigravity"),
        Path(".gemini/config/skills"),
        Path(".agents/skills"),
        Path(".gemini/config/mcp_config.json"),
        Path(".agents/mcp_config.json"),
        "mcp-json",
        "Google Antigravity CLI and IDE (agy)",
        detection_commands=("agy", "antigravity"),
        detection_globs=(
            "/Applications/Antigravity.app",
            "{home}/Applications/Antigravity.app",
            "{home}/AppData/Local/Programs/Antigravity/Antigravity.exe",
        ),
        project_detection_globs=("{project}/.agents/skills.json",),
    ),
    "gemini": AgentTarget(
        "gemini",
        ("gemini-cli",),
        Path(".agents/skills"),
        Path(".agents/skills"),
        Path(".gemini/settings.json"),
        Path(".gemini/settings.json"),
        "mcp-json",
        "Google Gemini CLI",
        (Path(".gemini/skills"),),
        (Path(".gemini/skills"),),
        detection_commands=("gemini",),
        project_detection_globs=(
            "{project}/GEMINI.md",
            "{project}/.gemini/commands",
        ),
    ),
    "copilot": AgentTarget(
        "copilot",
        ("github-copilot", "copilot-cli", "vscode", "vs-code"),
        Path(".agents/skills"),
        Path(".agents/skills"),
        description="GitHub Copilot CLI, VS Code, and JetBrains agent mode",
        retired_user_skill_roots=(Path(".copilot/skills"),),
        retired_project_skill_roots=(Path(".github/skills"),),
        detection_commands=("copilot", "github-copilot"),
        detection_globs=_extension_detection_globs("github.copilot-"),
        project_detection_globs=(
            "{project}/.github/copilot-instructions.md",
            "{project}/.github/instructions",
        ),
    ),
    "windsurf": AgentTarget(
        "windsurf",
        ("cascade", "devin-desktop"),
        Path(".agents/skills"),
        Path(".agents/skills"),
        Path(".codeium/windsurf/mcp_config.json"),
        Path(".windsurf/mcp_config.json"),
        "mcp-json",
        "Windsurf/Devin Desktop Cascade",
        (Path(".codeium/windsurf/skills"),),
        (Path(".windsurf/skills"),),
        detection_commands=("windsurf",),
        detection_globs=(
            "/Applications/Windsurf.app",
            "{home}/Applications/Windsurf.app",
            "{home}/AppData/Local/Programs/Windsurf/Windsurf.exe",
        ),
        project_detection_globs=(
            "{project}/.windsurfrules",
            "{project}/.windsurf/rules",
        ),
    ),
    "roo": AgentTarget(
        "roo",
        ("roo-code", "roocode"),
        Path(".agents/skills"),
        Path(".agents/skills"),
        description="Roo Code",
        retired_user_skill_roots=(Path(".roo/skills"),),
        retired_project_skill_roots=(Path(".roo/skills"),),
        detection_commands=("roo",),
        detection_globs=_extension_detection_globs(
            "rooveterinaryinc.roo-cline-", "rooveterinaryinc.roo-code-"
        ),
        project_detection_globs=(
            "{project}/.roomodes",
            "{project}/.roo/rules",
        ),
    ),
    "kilo": AgentTarget(
        "kilo",
        ("kilo-code", "kilocode"),
        Path(".agents/skills"),
        Path(".agents/skills"),
        description="Kilo Code",
        retired_user_skill_roots=(Path(".kilocode/skills"),),
        retired_project_skill_roots=(Path(".kilocode/skills"),),
        detection_commands=("kilo",),
        detection_globs=_extension_detection_globs(
            "kilocode.kilo-code-", "kilocode.kilocode-"
        ),
        project_detection_globs=(
            "{project}/.kilocodemodes",
            "{project}/.kilocode/rules",
        ),
    ),
}

DEFAULT_TARGET_NAMES = tuple(name for name in TARGETS if name != "shared")


def _alias_index():
    index = {}
    for target in TARGETS.values():
        index[target.name] = target.name
        for alias in target.aliases:
            index[alias] = target.name
    return index


ALIASES = _alias_index()


def _target_tokens(
    spec: Union[str, Sequence[str], None],
) -> List[str]:
    if spec is None:
        return ["detected"]
    if isinstance(spec, str):
        raw_names = [part.strip().lower() for part in spec.split(",")]
    else:
        raw_names = []
        for item in spec:
            raw_names.extend(part.strip().lower() for part in str(item).split(","))
    return [name for name in raw_names if name] or ["detected"]


def _uses_detection(spec: Union[str, Sequence[str], None]) -> bool:
    return any(name in DETECTED_TARGET_NAMES for name in _target_tokens(spec))


def resolve_targets(
    spec: Union[str, Sequence[str], None] = "all",
    detected_targets: Optional[Sequence[AgentTarget]] = None,
) -> List[AgentTarget]:
    """Resolve target names, ``all``, or a context-provided detected set."""

    raw_names = _target_tokens(spec)
    detection_names = [name for name in raw_names if name in DETECTED_TARGET_NAMES]
    if detection_names:
        if len(raw_names) > 1:
            raise ValueError(
                "'detected'/'auto' cannot be combined with named agent targets"
            )
        if detected_targets is None:
            raise ValueError(
                "'detected' target resolution requires local detection context"
            )
        canonical_names = []
        for target in detected_targets:
            if target.name not in canonical_names:
                canonical_names.append(target.name)
        if not canonical_names:
            canonical_names = ["shared"]
    elif "all" in raw_names:
        if len(raw_names) > 1:
            raise ValueError("'all' cannot be combined with named agent targets")
        canonical_names = list(DEFAULT_TARGET_NAMES)
    else:
        canonical_names = []
        unknown = []
        for name in raw_names:
            canonical = ALIASES.get(name)
            if canonical is None:
                unknown.append(name)
            elif canonical not in canonical_names:
                canonical_names.append(canonical)
        if unknown:
            supported = ", ".join(sorted(TARGETS))
            raise ValueError(
                "Unknown agent target(s): {}. Supported targets: {}".format(
                    ", ".join(unknown), supported
                )
            )

    return [TARGETS[name] for name in canonical_names]


def _detection_matches(
    pattern: str,
    home: Path,
    project_dir: Path,
) -> List[str]:
    expanded = pattern.format(home=str(home), project=str(project_dir))
    return sorted(glob.glob(os.path.expanduser(expanded)))


# @sds-trace: agent_integration.install_agents:AC-5
def detect_agent_targets(
    home: Optional[Path] = None,
    project_dir: Optional[Path] = None,
    which=None,
) -> List[AgentDetection]:
    """Conservatively detect locally used agents without SDS-created markers."""

    home = Path.home() if home is None else Path(home)
    project_dir = Path.cwd() if project_dir is None else Path(project_dir)
    which = shutil.which if which is None else which
    detections = []

    for target in TARGETS.values():
        if target.name == "shared":
            continue
        evidence = []
        for command in target.detection_commands:
            executable = which(command)
            if executable:
                evidence.append("command:{}={}".format(command, executable))
        for pattern in target.detection_globs + target.project_detection_globs:
            matches = _detection_matches(pattern, home, project_dir)
            if matches:
                evidence.append("path:{}".format(matches[0]))
        if evidence:
            detections.append(AgentDetection(target, tuple(evidence)))

    return detections


def _default_skill_source() -> Path:
    packaged = Path(__file__).resolve().parent / "_skill" / SKILL_NAME
    if (packaged / "SKILL.md").is_file():
        return packaged

    # Source checkout layout: skills/sds-core/src/sds/agent_install.py
    checkout = Path(__file__).resolve().parents[2]
    if (checkout / "SKILL.md").is_file():
        return checkout
    raise FileNotFoundError(
        "The packaged SDS Agent Skill was not found. Reinstall sds-cli from a "
        "complete release artifact."
    )


def _bundle_entries(source: Path) -> List[Tuple[Path, Path]]:
    source = Path(source)
    skill_file = source / "SKILL.md"
    if not skill_file.is_file():
        raise FileNotFoundError("Skill source has no SKILL.md: {}".format(source))

    entries = [(skill_file, Path("SKILL.md"))]
    for folder_name in ("templates", "references"):
        folder = source / folder_name
        if not folder.exists() and folder_name == "references":
            # In a source checkout, references live at repository root.
            candidate = source.parents[1] / "references" if len(source.parents) > 1 else folder
            if candidate.is_dir():
                folder = candidate
        if folder.is_dir():
            for item in sorted(folder.rglob("*")):
                if item.is_file():
                    entries.append((item, Path(folder_name) / item.relative_to(folder)))
    return entries


def _hash_entries(entries: Iterable[Tuple[Path, Path]]) -> str:
    digest = hashlib.sha256()
    for source, relative in sorted(entries, key=lambda entry: entry[1].as_posix()):
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(source.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _hash_installed_bundle(destination: Path) -> str:
    entries = []
    for item in sorted(destination.rglob("*")):
        if item.is_file() and item.name != MANAGED_MARKER:
            entries.append((item, item.relative_to(destination)))
    return _hash_entries(entries)


def _read_marker(destination: Path):
    marker_path = destination / MANAGED_MARKER
    if not marker_path.is_file():
        return None
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(marker, dict):
        return None
    if marker.get("managed_by") != "sds-cli" or marker.get("skill") != SKILL_NAME:
        return None
    return marker


def _write_marker(destination: Path, bundle_hash: str, bundle_version: str):
    # @sds-trace: agent_integration.install_agents:AC-6
    marker = {
        "managed_by": "sds-cli",
        "skill": SKILL_NAME,
        "bundle_version": bundle_version,
        "bundle_hash": bundle_hash,
    }
    _atomic_write_text(
        destination / MANAGED_MARKER,
        json.dumps(marker, indent=2, sort_keys=True) + "\n",
    )


def _copy_bundle(
    entries,
    destination: Path,
    bundle_hash: str,
    bundle_version: str,
):
    for source, relative in entries:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source), str(target))
    _write_marker(destination, bundle_hash, bundle_version)


def _atomic_install_bundle(
    destination: Path,
    entries,
    bundle_hash: str,
    bundle_version: str,
    force: bool,
    dry_run: bool,
) -> Tuple[str, str]:
    if destination.exists() and not destination.is_dir():
        return "error", "destination exists but is not a directory"

    if destination.is_dir():
        marker = _read_marker(destination)
        installed_hash = _hash_installed_bundle(destination)
        if installed_hash == bundle_hash:
            if marker is None:
                return "unchanged", "user-owned skill content is already current"
            if (
                marker.get("bundle_hash") == bundle_hash
                and marker.get("bundle_version") == bundle_version
            ):
                return (
                    "unchanged",
                    "skill bundle {} is already current".format(bundle_version),
                )
            if dry_run:
                return (
                    "planned",
                    "would update managed skill metadata to {}".format(
                        bundle_version
                    ),
                )
            _write_marker(destination, bundle_hash, bundle_version)
            return (
                "changed",
                "updated managed skill metadata to {}".format(bundle_version),
            )
        if marker is None and not force:
            return "skipped", "existing user-owned skill was preserved (use --force to replace)"
        if marker is not None:
            recorded_hash = marker.get("bundle_hash")
            if recorded_hash and recorded_hash != installed_hash and not force:
                return (
                    "skipped",
                    "locally modified managed skill was preserved (use --force to replace)",
                )

    if dry_run:
        verb = "replace" if destination.exists() else "install"
        return "planned", "would {} managed skill bundle".format(verb)

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=".{}-sds-install-".format(SKILL_NAME), dir=str(destination.parent))
    )
    backup = destination.parent / ".{}-sds-backup-{}".format(
        SKILL_NAME, uuid.uuid4().hex
    )
    try:
        _copy_bundle(entries, temporary, bundle_hash, bundle_version)
        if destination.exists():
            destination.rename(backup)
        temporary.rename(destination)
        if backup.exists():
            shutil.rmtree(str(backup))
    except Exception:
        if destination.exists() and backup.exists():
            shutil.rmtree(str(destination))
        if backup.exists() and not destination.exists():
            backup.rename(destination)
        raise
    finally:
        if temporary.exists():
            shutil.rmtree(str(temporary))
    return "changed", "installed managed skill bundle {}".format(bundle_version)


def _retire_managed_bundle(
    destination: Path,
    force: bool,
    dry_run: bool,
) -> Optional[Tuple[str, str]]:
    """Remove a redundant legacy copy only when SDS can prove ownership."""

    if not destination.exists():
        return None
    if not destination.is_dir():
        return "skipped", "retired skill path is user-owned and was preserved"

    marker = _read_marker(destination)
    if marker is None:
        return "skipped", "retired user-owned skill was preserved"

    installed_hash = _hash_installed_bundle(destination)
    recorded_hash = marker.get("bundle_hash")
    if (not recorded_hash or recorded_hash != installed_hash) and not force:
        return (
            "skipped",
            "locally modified retired skill was preserved (use --force to remove)",
        )

    if dry_run:
        return "planned", "would remove redundant managed skill bundle"

    shutil.rmtree(str(destination))
    return "changed", "removed redundant managed skill bundle"


def _atomic_write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temp = tempfile.mkstemp(
        prefix=".{}-".format(path.name), suffix=".tmp", dir=str(path.parent)
    )
    temp_path = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        if path.exists():
            os.chmod(str(temp_path), path.stat().st_mode)
        os.replace(str(temp_path), str(path))
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _install_json_mcp(
    path: Path,
    command: str,
    style: str,
    force: bool,
    dry_run: bool,
) -> Tuple[str, str]:
    if path.exists():
        if not path.is_file():
            return "error", "MCP configuration path is not a file"
        try:
            content = path.read_text(encoding="utf-8")
            # Some clients create a zero-byte configuration placeholder before
            # the first MCP server is added. Treat that initial state as an
            # empty object while continuing to preserve malformed non-empty
            # configuration for manual recovery.
            # @sds-trace: agent_integration.install_agents:AC-3
            document = {} if not content.strip() else json.loads(content)
        except (OSError, ValueError) as exc:
            return "error", "invalid JSON was preserved: {}".format(exc)
        if not isinstance(document, dict):
            return "error", "JSON root must be an object; existing file was preserved"
    else:
        document = {}

    if style == "opencode-json":
        mcp = document.setdefault("mcp", {})
        if not isinstance(mcp, dict):
            return "error", "existing 'mcp' value is not an object"
        servers = mcp.setdefault("servers", {})
        if not isinstance(servers, dict):
            return "error", "existing 'mcp.servers' value is not an object"
        desired = {"type": "local", "command": [command, "mcp"]}
    else:
        servers = document.setdefault("mcpServers", {})
        if not isinstance(servers, dict):
            return "error", "existing 'mcpServers' value is not an object"
        desired = {"command": command, "args": ["mcp"]}

    existing = servers.get(SKILL_NAME)
    if existing == desired:
        return "unchanged", "MCP server is already current"
    # Earlier SDS releases emitted one exact, SDS-only shape for each JSON
    # style. A path change in that shape is an installer upgrade, not a
    # user-owned conflict. Any additional fields or behavior remain preserved.
    # @sds-trace: agent_integration.install_agents:AC-7
    canonical_upgrade = _is_canonical_legacy_json_mcp(existing, style)
    if existing is not None and not force and not canonical_upgrade:
        return "skipped", "existing user-owned 'sds' MCP entry was preserved"
    if dry_run:
        if canonical_upgrade:
            return "planned", "would advance canonical SDS MCP server command"
        return "planned", "would {} MCP server entry".format(
            "replace" if existing is not None else "add"
        )

    servers[SKILL_NAME] = desired
    _atomic_write_text(path, json.dumps(document, indent=2, ensure_ascii=False) + "\n")
    if canonical_upgrade:
        return "changed", "advanced canonical SDS MCP server command"
    return "changed", "configured SDS MCP server"


def _command_basename(command: object) -> str:
    if not isinstance(command, str):
        return ""
    return command.replace("\\", "/").rsplit("/", 1)[-1].lower()


def _is_canonical_legacy_json_mcp(existing: object, style: str) -> bool:
    """Return whether an entry is exactly an SDS shape emitted by this CLI."""

    if not isinstance(existing, dict):
        return False
    if style == "opencode-json":
        if set(existing) != {"type", "command"} or existing.get("type") != "local":
            return False
        invocation = existing.get("command")
        if not isinstance(invocation, list) or len(invocation) != 2:
            return False
        executable, argument = invocation
    else:
        if set(existing) != {"command", "args"}:
            return False
        executable = existing.get("command")
        arguments = existing.get("args")
        if arguments != ["mcp"]:
            return False
        argument = "mcp"
    return argument == "mcp" and _command_basename(executable) in {"sds", "sds.exe"}


def _codex_mcp_block(command: str) -> str:
    # JSON string/array syntax is also valid TOML syntax for these values.
    return "\n".join(
        (
            TOML_BLOCK_START,
            "[mcp_servers.sds]",
            "command = {}".format(json.dumps(command)),
            'args = ["mcp"]',
            TOML_BLOCK_END,
        )
    )


def _install_codex_mcp(
    path: Path, command: str, force: bool, dry_run: bool
) -> Tuple[str, str]:
    if path.exists():
        if not path.is_file():
            return "error", "Codex configuration path is not a file"
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            return "error", "could not read Codex configuration: {}".format(exc)
    else:
        content = ""

    desired = _codex_mcp_block(command)
    block_pattern = re.compile(
        re.escape(TOML_BLOCK_START)
        + r".*?"
        + re.escape(TOML_BLOCK_END),
        flags=re.DOTALL,
    )
    managed = block_pattern.search(content)
    if managed:
        if managed.group(0) == desired:
            return "unchanged", "MCP server is already current"
        updated = content[: managed.start()] + desired + content[managed.end() :]
    else:
        if TOML_BLOCK_START in content or TOML_BLOCK_END in content:
            return "error", "incomplete SDS-managed TOML block was preserved"
        if re.search(r"(?m)^\s*\[mcp_servers\.sds\]\s*(?:#.*)?$", content):
            if not force:
                return "skipped", "existing user-owned Codex 'sds' MCP table was preserved"
            return (
                "skipped",
                "Codex user-owned TOML tables are not rewritten automatically; remove it first",
            )
        separator = "" if not content else ("\n" if content.endswith("\n") else "\n\n")
        updated = content + separator + desired + "\n"

    if dry_run:
        return "planned", "would configure SDS MCP server"
    _atomic_write_text(path, updated)
    return "changed", "configured SDS MCP server"


def _target_root(
    target: AgentTarget, scope: str, home: Path, project_dir: Path
) -> Path:
    base = home if scope == "user" else project_dir
    relative = target.user_skill_root if scope == "user" else target.project_skill_root
    return base / relative


def _target_mcp_path(
    target: AgentTarget, scope: str, home: Path, project_dir: Path
) -> Optional[Path]:
    relative = target.user_mcp_path if scope == "user" else target.project_mcp_path
    if relative is None:
        return None
    return (home if scope == "user" else project_dir) / relative


def _retired_skill_roots(target: AgentTarget, scope: str) -> Tuple[Path, ...]:
    if scope == "user":
        return target.retired_user_skill_roots
    return target.retired_project_skill_roots


def install_agent_integrations(
    home: Optional[Path] = None,
    project_dir: Optional[Path] = None,
    scope: str = "user",
    targets: Union[str, Sequence[str], None] = "detected",
    command: str = "sds",
    configure_mcp: bool = True,
    force: bool = False,
    dry_run: bool = False,
    skill_source: Optional[Path] = None,
) -> InstallSummary:
    """Install the SDS skill and optionally its MCP server registrations."""

    if scope not in ("user", "project"):
        raise ValueError("scope must be 'user' or 'project'")
    home = Path.home() if home is None else Path(home)
    project_dir = Path.cwd() if project_dir is None else Path(project_dir)
    source = _default_skill_source() if skill_source is None else Path(skill_source)
    entries = _bundle_entries(source)
    bundle_hash = _hash_entries(entries)
    detection_mode = _uses_detection(targets)
    detections = (
        detect_agent_targets(home=home, project_dir=project_dir)
        if detection_mode
        else []
    )
    selected = resolve_targets(
        targets,
        detected_targets=[detection.target for detection in detections],
    )
    summary = InstallSummary(
        selection_mode="detected" if detection_mode else "explicit",
        selected_targets=tuple(target.name for target in selected),
        detections=detections,
    )

    installed_skill_results = {}
    configured_mcp_paths = set()
    for target in selected:
        skill_path = _target_root(target, scope, home, project_dir) / SKILL_NAME
        skill_key = os.path.normcase(str(skill_path.resolve(strict=False)))
        if skill_key not in installed_skill_results:
            try:
                status, message = _atomic_install_bundle(
                    skill_path,
                    entries,
                    bundle_hash,
                    SKILL_BUNDLE_VERSION,
                    force,
                    dry_run,
                )
            except Exception as exc:
                status, message = "error", "skill installation failed: {}".format(exc)
            installed_skill_results[skill_key] = (status, message)
            summary.events.append(
                InstallEvent(target.name, "skill", skill_path, status, message)
            )
        else:
            status, _ = installed_skill_results[skill_key]
            summary.events.append(
                InstallEvent(
                    target.name,
                    "skill",
                    skill_path,
                    status if status in ("error", "skipped") else "unchanged",
                    "shared skill bundle already handled by another target",
                )
            )

        # @sds-trace: agent_integration.install_agents:AC-4
        if status in ("changed", "unchanged", "planned"):
            base = home if scope == "user" else project_dir
            for retired_root in _retired_skill_roots(target, scope):
                retired_path = base / retired_root / SKILL_NAME
                retired_key = os.path.normcase(
                    str(retired_path.resolve(strict=False))
                )
                if retired_key == skill_key:
                    continue
                try:
                    retired_result = _retire_managed_bundle(
                        retired_path, force, dry_run
                    )
                except Exception as exc:
                    retired_result = (
                        "error",
                        "retired skill cleanup failed: {}".format(exc),
                    )
                if retired_result is not None:
                    retired_status, retired_message = retired_result
                    summary.events.append(
                        InstallEvent(
                            target.name,
                            "cleanup",
                            retired_path,
                            retired_status,
                            retired_message,
                        )
                    )

        if not configure_mcp or not target.mcp_style:
            continue
        mcp_path = _target_mcp_path(target, scope, home, project_dir)
        if mcp_path is None:
            continue
        mcp_key = os.path.normcase(str(mcp_path.resolve(strict=False)))
        if mcp_key in configured_mcp_paths:
            summary.events.append(
                InstallEvent(
                    target.name,
                    "mcp",
                    mcp_path,
                    "unchanged",
                    "shared MCP configuration already handled by another target",
                )
            )
            continue
        configured_mcp_paths.add(mcp_key)
        try:
            if target.mcp_style == "codex-toml":
                status, message = _install_codex_mcp(
                    mcp_path, command, force, dry_run
                )
            else:
                status, message = _install_json_mcp(
                    mcp_path, command, target.mcp_style, force, dry_run
                )
        except Exception as exc:
            status, message = "error", "MCP configuration failed: {}".format(exc)
        summary.events.append(
            InstallEvent(target.name, "mcp", mcp_path, status, message)
        )
    return summary


def _default_command() -> str:
    executable = shutil.which("sds")
    return str(Path(executable).resolve()) if executable else "sds"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sds install-agents",
        description="Install SDS into supported coding agents and IDEs.",
    )
    parser.add_argument(
        "--targets",
        default="detected",
        help=(
            "'detected'/'auto' (default), 'all', or comma-separated targets "
            "(agy is an alias for antigravity)"
        ),
    )
    parser.add_argument(
        "--scope", choices=("user", "project"), default="user"
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project root used with --scope project (default: current directory)",
    )
    parser.add_argument(
        "--command",
        default=_default_command(),
        help="sds executable stored in MCP configurations",
    )
    parser.add_argument(
        "--no-mcp", action="store_true", help="Install Agent Skills without MCP entries"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace conflicting skill copies/MCP entries where safe",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without writing files"
    )
    return parser


def _print_summary(summary: InstallSummary):
    labels = {
        "changed": "PASS",
        "planned": "PLAN",
        "unchanged": "OK",
        "skipped": "WARN",
        "error": "FAIL",
    }
    print("[INFO] SDS Skill bundle version: {}".format(SKILL_BUNDLE_VERSION))
    if summary.selection_mode == "detected":
        if summary.detections:
            print(
                "[INFO] Detected agent targets: {}".format(
                    ", ".join(
                        detection.target.name for detection in summary.detections
                    )
                )
            )
            for detection in summary.detections:
                print(
                    "[INFO] {} detection evidence: {}".format(
                        detection.target.name,
                        ", ".join(detection.evidence),
                    )
                )
        else:
            print(
                "[INFO] No specific agent detected; using the shared Skill path only."
            )

    for event in summary.events:
        print(
            "[{label}] {target} {kind}: {message} ({path})".format(
                label=labels[event.status],
                target=event.target,
                kind=event.kind,
                message=event.message,
                path=event.path,
            )
        )
    print(
        "Agent integration summary: {} changed, {} planned, {} current, {} "
        "preserved, {} failed.".format(
            summary.changed,
            summary.planned,
            summary.unchanged,
            summary.skipped,
            len(summary.errors),
        )
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = install_agent_integrations(
            project_dir=args.project_dir,
            scope=args.scope,
            targets=args.targets,
            command=args.command,
            configure_mcp=not args.no_mcp,
            force=args.force,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))
        return 2
    _print_summary(summary)
    return 0 if summary.ok else 1


if __name__ == "__main__":
    sys.exit(main())
