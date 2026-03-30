#!/usr/bin/env bash
# =============================================================================
# setup.sh — Chișinău Urban Traffic Simulation
# Sets up a Python virtual environment and installs all dependencies.
#
# Usage:
#   bash setup.sh              # create venv at ./venv and install deps
#   bash setup.sh --rebuild    # delete existing venv and start fresh
# =============================================================================

set -euo pipefail

VENV_DIR="venv"
PYTHON="${PYTHON:-python3}"
REQUIREMENTS="requirements.txt"

# ── colours ──────────────────────────────────────────────────────────
GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RED="\033[0;31m"; NC="\033[0m"
info()    { echo -e "${GREEN}[setup]${NC} $*"; }
warning() { echo -e "${YELLOW}[setup]${NC} $*"; }
error()   { echo -e "${RED}[setup]${NC} $*" >&2; exit 1; }

# ── args ─────────────────────────────────────────────────────────────
REBUILD=false
for arg in "$@"; do
  [[ "$arg" == "--rebuild" ]] && REBUILD=true
done

# ── rebuild guard ────────────────────────────────────────────────────
if [[ "$REBUILD" == true && -d "$VENV_DIR" ]]; then
  warning "Removing existing virtual environment at ./$VENV_DIR ..."
  rm -rf "$VENV_DIR"
fi

# ── python check ─────────────────────────────────────────────────────
command -v "$PYTHON" >/dev/null 2>&1 \
  || error "Python not found. Install Python 3.9+ and retry."

PY_VERSION=$("$PYTHON" -c "import sys; print('%d.%d' % sys.version_info[:2])")
PY_MAJOR=$("$PYTHON" -c "import sys; print(sys.version_info[0])")
PY_MINOR=$("$PYTHON" -c "import sys; print(sys.version_info[1])")

if [[ "$PY_MAJOR" -lt 3 || ("$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 9) ]]; then
  error "Python 3.9+ required (found $PY_VERSION)."
fi
info "Using Python $PY_VERSION  ($($PYTHON -c 'import sys; print(sys.executable)'))"

# ── create venv ──────────────────────────────────────────────────────
if [[ ! -d "$VENV_DIR" ]]; then
  info "Creating virtual environment at ./$VENV_DIR ..."
  "$PYTHON" -m venv "$VENV_DIR"
else
  info "Virtual environment already exists at ./$VENV_DIR — skipping creation."
  info "Run with --rebuild to recreate from scratch."
fi

# ── activate ─────────────────────────────────────────────────────────
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
info "Virtual environment activated."

# ── upgrade pip ──────────────────────────────────────────────────────
info "Upgrading pip ..."
pip install --quiet --upgrade pip

# ── install deps ─────────────────────────────────────────────────────
[[ -f "$REQUIREMENTS" ]] || error "$REQUIREMENTS not found."
info "Installing dependencies from $REQUIREMENTS ..."
pip install --quiet -r "$REQUIREMENTS"

# ── SUMO_HOME check ──────────────────────────────────────────────────
echo ""
if [[ -z "${SUMO_HOME:-}" ]]; then
  warning "SUMO_HOME is not set."
  warning "Install SUMO and add the following to your shell profile:"
  warning ""
  warning "  # Linux:"
  warning "  export SUMO_HOME=/usr/share/sumo"
  warning ""
  warning "  # macOS (Homebrew):"
  warning "  export SUMO_HOME=/opt/homebrew/share/sumo"
  warning ""
  warning "  # Windows: set SUMO_HOME=C:\\Program Files (x86)\\Eclipse\\Sumo"
else
  info "SUMO_HOME is set → $SUMO_HOME"
  if command -v sumo >/dev/null 2>&1; then
    info "SUMO binary found: $(command -v sumo)"
  else
    warning "sumo binary not found in PATH — check your SUMO installation."
  fi
fi

# ── done ─────────────────────────────────────────────────────────────
echo ""
info "Setup complete. To activate the environment in a new shell:"
echo ""
echo "    source $VENV_DIR/bin/activate"
echo ""
info "Then run:"
echo ""
echo "    python scripts/prepare_map.py   # download Chișinău map (once)"
echo "    python main.py                  # run the simulation"
echo "    python main.py --gui            # with SUMO visual interface"
echo "    pytest tests/                   # run all tests"
echo ""
