import sys
from pathlib import Path
from sds import sds_self_check
from sds import mcp

def print_usage():
    print("SDS (Spec-Defined Software) Next-Gen Command Line Tool")
    print("\nUsage:")
    print("  sds check                      - Run SDS baseline validation & drift verification")
    print("  sds init                       - Scaffold new SDS directories, templates, and config")
    print("  sds install-hook               - Install Git pre-commit drift guard hook")
    print("  sds refresh-harness            - Safely refresh the project harness configurations")
    print("  sds mcp                        - Run standard-compliant JSON-RPC MCP server")
    print("  sds version                    - Print sds-cli version")
    print("\nLegacy flags:")
    print("  sds --init, sds --install-hook, sds --refresh-harness, sds --version")

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
        elif arg == "check":
            sds_self_check.validate_sds(cwd_path)
            sys.exit(0)
        elif arg in ("mcp", "--mcp"):
            mcp.main()
            sys.exit(0)
        elif arg in ("version", "--version"):
            print(f"sds-cli version {sds_self_check.HARNESS_VERSION}")
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
