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

# 2. Decide installation path (pipx vs isolated venv)
if command -v pipx >/dev/null 2>&1; then
    print_info "Found pipx! Installing globally and isolating dependencies..."
    set +e
    pipx install git+https://github.com/your-org/spec-defined-software.git --force >/dev/null 2>&1
    PIPX_STATUS=$?
    set -e
    if [ $PIPX_STATUS -eq 0 ]; then
        print_success "SDS CLI successfully installed via pipx!"
        echo ""
        echo "Try running:"
        echo "  ${COLOR_BOLD}sds check${COLOR_RESET} (or sds --help)"
        echo ""
        exit 0
    else
        print_warn "pipx installation failed. Falling back to isolated virtualenv..."
    fi
fi

# 3. Fallback: Create isolated venv in ~/.sds/venv
INSTALL_DIR="$HOME/.sds"
VENV_DIR="$INSTALL_DIR/venv"
BIN_DIR="$HOME/.local/bin"

print_info "Setting up isolated sandbox environment in $VENV_DIR..."
mkdir -p "$INSTALL_DIR"

# Create venv
python3 -m venv "$VENV_DIR"
print_success "Isolated virtualenv created."

# Upgrade pip and install package
print_info "Installing sds-cli package..."
"$VENV_DIR/bin/pip" install --upgrade pip >/dev/null 2>&1
"$VENV_DIR/bin/pip" install git+https://github.com/your-org/spec-defined-software.git >/dev/null 2>&1
print_success "Package installed successfully."

# 4. Create symlink in ~/.local/bin
mkdir -p "$BIN_DIR"
rm -f "$BIN_DIR/sds"
ln -s "$VENV_DIR/bin/sds" "$BIN_DIR/sds"
print_success "Symlink created at: $BIN_DIR/sds"

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
