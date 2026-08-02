import sys
from pathlib import Path
from sds import __version__
from sds import sds_self_check
from sds import mcp
from sds import agent_install


def print_usage():
    print("SDS (Spec-Defined Software) Next-Gen Command Line Tool")
    print("\nUsage:")
    print("  sds check                      - Run SDS baseline validation & drift verification")
    print("  sds init                       - Scaffold new SDS directories, templates, and config")
    print("  sds install-hook               - Install Git pre-commit drift guard hook")
    print("  sds refresh-harness            - Safely refresh the project harness configurations")
    print("  sds install-agents [options]   - Install SDS Skill/MCP into coding agents and IDEs")
    print("  sds mcp                        - Run standard-compliant JSON-RPC MCP server")
    print("  sds version                    - Print CLI, harness, and Skill versions")
    print("\nLegacy flags:")
    print("  sds --init, sds --install-hook, sds --refresh-harness, sds --version")


# @sds-trace: agent_integration.install_agents:AC-6
def version_report():
    return "\n".join(
        (
            f"sds-cli version {__version__}",
            f"SDS harness version {sds_self_check.HARNESS_VERSION}",
            f"SDS Skill bundle version {agent_install.SKILL_BUNDLE_VERSION}",
        )
    )


def main():
    cwd_path = Path.cwd()
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("init", "--init"):
            sds_self_check.initialize_sds_project(cwd_path)
            sys.exit(0)
        elif arg in ("install-hook", "--install-hook"):
            sds_self_check.install_git_hook(cwd_path)
            sys.exit(0)
        elif arg in ("refresh-harness", "--refresh-harness"):
            sys.exit(sds_self_check.refresh_project_harness(cwd_path))
        elif arg in ("install-agents", "--install-agents"):
            sys.exit(agent_install.main(sys.argv[2:]))
        elif arg == "check":
            sds_self_check.validate_sds(cwd_path)
            sys.exit(0)
        elif arg in ("mcp", "--mcp"):
            mcp.main()
            sys.exit(0)
        elif arg in ("version", "--version"):
            print(version_report())
            sys.exit(0)
        elif arg in ("help", "--help", "-h"):
            print_usage()
            sys.exit(0)
        else:
            sds_self_check.print_error(f"Unknown command or argument: {sys.argv[1]}")
            print_usage()
            sys.exit(1)
    else:
        # Default behavior matches legacy check trigger
        sds_self_check.validate_sds(cwd_path)

if __name__ == "__main__":
    main()
