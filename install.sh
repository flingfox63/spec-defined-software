#!/bin/sh
# SDS (Spec-Defined Software) macOS/Linux One-Click Installer

set -e

# --- Styles ---
COLOR_BLUE='\033[94m'
COLOR_GREEN='\033[92m'
COLOR_YELLOW='\033[93m'
COLOR_RED='\033[91m'
COLOR_BOLD='\033[1m'
COLOR_RESET='\033[0m'

print_info() {
    printf "${COLOR_BLUE}[INFO]${COLOR_RESET} %s\n" "$1"
}

print_success() {
    printf "${COLOR_GREEN}${COLOR_BOLD}[PASS]${COLOR_RESET} %s\n" "$1"
}

print_warn() {
    printf "${COLOR_YELLOW}[WARN]${COLOR_RESET} %s\n" "$1"
}

print_error() {
    printf "${COLOR_RED}${COLOR_BOLD}[FAIL]${COLOR_RESET} %s\n" "$1" >&2
}

resolve_pipx_sds_command() {
    SDS_PIPX_VENVS=$(pipx environment --value PIPX_LOCAL_VENVS 2>/dev/null || :)
    if [ -n "$SDS_PIPX_VENVS" ]; then
        SDS_PIPX_CANDIDATE="$SDS_PIPX_VENVS/sds-cli/bin/sds"
        if [ -f "$SDS_PIPX_CANDIDATE" ] && [ -x "$SDS_PIPX_CANDIDATE" ]; then
            printf '%s\n' "$SDS_PIPX_CANDIDATE"
            return 0
        fi
    fi

    SDS_PIPX_BIN=$(pipx environment --value PIPX_BIN_DIR 2>/dev/null || :)
    if [ -n "$SDS_PIPX_BIN" ]; then
        SDS_PIPX_CANDIDATE="$SDS_PIPX_BIN/sds"
        if [ -f "$SDS_PIPX_CANDIDATE" ] && [ -x "$SDS_PIPX_CANDIDATE" ]; then
            printf '%s\n' "$SDS_PIPX_CANDIDATE"
            return 0
        fi
    fi

    SDS_PIPX_CANDIDATE="$HOME/.local/bin/sds"
    if [ -f "$SDS_PIPX_CANDIDATE" ] && [ -x "$SDS_PIPX_CANDIDATE" ]; then
        printf '%s\n' "$SDS_PIPX_CANDIDATE"
        return 0
    fi

    SDS_PIPX_CANDIDATE=$(command -v sds 2>/dev/null || :)
    if [ -n "$SDS_PIPX_CANDIDATE" ] && [ -f "$SDS_PIPX_CANDIDATE" ] && [ -x "$SDS_PIPX_CANDIDATE" ]; then
        case "$SDS_PIPX_CANDIDATE" in
            /*)
                printf '%s\n' "$SDS_PIPX_CANDIDATE"
                ;;
            *)
                SDS_PIPX_COMMAND_DIR=$(CDPATH= cd "$(dirname "$SDS_PIPX_CANDIDATE")" 2>/dev/null && pwd -P) || return 1
                printf '%s/%s\n' "$SDS_PIPX_COMMAND_DIR" "$(basename "$SDS_PIPX_CANDIDATE")"
                ;;
        esac
        return 0
    fi

    return 1
}

install_agent_integrations() {
    SDS_AGENT_COMMAND=$1

    if [ ! -f "$SDS_AGENT_COMMAND" ] || [ ! -x "$SDS_AGENT_COMMAND" ]; then
        print_error "The installed SDS executable could not be found at: $SDS_AGENT_COMMAND"
        return 1
    fi

    print_info "Installing SDS integrations for supported agents and IDEs..."
    if "$SDS_AGENT_COMMAND" install-agents --targets detected --command "$SDS_AGENT_COMMAND"; then
        print_success "Agent and IDE integrations installed successfully."
    else
        SDS_AGENT_STATUS=$?
        print_error "SDS CLI was installed, but agent integration failed (exit code $SDS_AGENT_STATUS)."
        print_error "Re-run: \"$SDS_AGENT_COMMAND\" install-agents --targets detected --command \"$SDS_AGENT_COMMAND\""
        return "$SDS_AGENT_STATUS"
    fi
}

# --- Welcome Banner ---
echo ""
echo "${COLOR_BLUE}${COLOR_BOLD}==================================================${COLOR_RESET}"
echo "    🚀  SDS (Spec-Defined Software) Installer      "
echo "${COLOR_BLUE}${COLOR_BOLD}==================================================${COLOR_RESET}"
echo ""

# 1. Check Python 3
if ! command -v python3 >/dev/null 2>&1; then
    print_error "Python 3 is required but could not be found in your PATH."
    print_error "Please install Python 3 and try again."
    exit 1
fi
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
print_success "Found Python 3 (v$PYTHON_VERSION)"

# 1.5 Determine installation source (local vs remote). Only the repository that
# contains this installer is eligible for a local development install. This
# avoids installing an unrelated project merely because the current directory
# also contains a pyproject.toml.
INSTALL_SOURCE="git+https://github.com/flingfox63/spec-defined-software.git"
SCRIPT_DIR=""
if [ -f "$0" ]; then
    SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" 2>/dev/null && pwd -P) || SCRIPT_DIR=""
fi

if [ -n "$SCRIPT_DIR" ] \
    && [ -f "$SCRIPT_DIR/pyproject.toml" ] \
    && [ -f "$SCRIPT_DIR/skills/sds-core/src/sds/cli.py" ] \
    && grep -Eq "^[[:space:]]*name[[:space:]]*=[[:space:]]*['\"]sds-cli['\"][[:space:]]*(#.*)?$" "$SCRIPT_DIR/pyproject.toml"; then
    print_info "Detected the local SDS repository at $SCRIPT_DIR."
    INSTALL_SOURCE="$SCRIPT_DIR"
fi

# 2. Decide installation path (pipx vs isolated venv)
if command -v pipx >/dev/null 2>&1; then
    print_info "Found pipx! Installing globally and isolating dependencies..."
    if pipx install "$INSTALL_SOURCE" --force; then
        SDS_COMMAND=$(resolve_pipx_sds_command || :)
        if [ -z "$SDS_COMMAND" ]; then
            print_error "SDS was installed via pipx, but its executable path could not be resolved."
            exit 1
        fi

        install_agent_integrations "$SDS_COMMAND"
        print_success "SDS CLI successfully installed via pipx!"
        echo ""
        echo "Try running:"
        echo "  ${COLOR_BOLD}$SDS_COMMAND check${COLOR_RESET} (or $SDS_COMMAND --help)"
        echo ""
        exit 0
    else
        PIPX_STATUS=$?
        print_warn "pipx installation failed (exit code $PIPX_STATUS). Falling back to isolated virtualenv..."
    fi
fi

# 3. Fallback: Create isolated venv in ~/.sds/venv
INSTALL_DIR="$HOME/.sds"
VENV_DIR="$INSTALL_DIR/venv"
BIN_DIR="$HOME/.local/bin"

print_info "Setting up isolated sandbox environment in $VENV_DIR..."
mkdir -p "$INSTALL_DIR"

# Create venv
if ! python3 -m venv "$VENV_DIR"; then
    print_error "Could not create the isolated virtualenv at $VENV_DIR."
    exit 1
fi
print_success "Isolated virtualenv created."

# Upgrade pip and install package
print_info "Installing sds-cli package..."
if ! "$VENV_DIR/bin/pip" install --upgrade pip; then
    print_error "Could not upgrade pip in the isolated SDS environment."
    exit 1
fi
if ! "$VENV_DIR/bin/pip" install "$INSTALL_SOURCE"; then
    print_error "Could not install sds-cli from $INSTALL_SOURCE."
    exit 1
fi
print_success "Package installed successfully."

SDS_COMMAND="$VENV_DIR/bin/sds"
if [ ! -f "$SDS_COMMAND" ] || [ ! -x "$SDS_COMMAND" ]; then
    print_error "Package installation completed, but the SDS executable is missing at $SDS_COMMAND."
    exit 1
fi

# 4. Create symlink in ~/.local/bin
mkdir -p "$BIN_DIR"
rm -f "$BIN_DIR/sds"
ln -s "$VENV_DIR/bin/sds" "$BIN_DIR/sds"
print_success "Symlink created at: $BIN_DIR/sds"

# 5. Install integrations only after the exact executable path is known. The
# same absolute path is persisted into generated MCP configurations.
install_agent_integrations "$SDS_COMMAND"

# --- Output Path Verification ---
echo ""
echo "${COLOR_GREEN}${COLOR_BOLD}==================================================${COLOR_RESET}"
echo "    🎉  SDS Installation Completed Successfully!   "
echo "${COLOR_GREEN}${COLOR_BOLD}==================================================${COLOR_RESET}"
echo ""

# Check if ~/.local/bin is in PATH
case ":$PATH:" in
    *:"$BIN_DIR":*)
        print_success "SDS is ready! Run: ${COLOR_BOLD}sds check${COLOR_RESET}"
        ;;
    *)
        print_warn "$BIN_DIR is not in your shell PATH."
        echo "Please add the following line to your shell profile (.bashrc, .zshrc, etc.):"
        echo "  ${COLOR_BOLD}export PATH=\"\$HOME/.local/bin:\$PATH\"${COLOR_RESET}"
        echo "Then restart your terminal and run: ${COLOR_BOLD}sds check${COLOR_RESET}"
        ;;
esac
echo ""
