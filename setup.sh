#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Colour

info()    { echo -e "${GREEN}[VoiceDoc]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║      VoiceDoc — Setup Script          ║"
echo "║  Offline AI for Community Health      ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# ---------------------------------------------------------------------------
# 1. Check Python 3.10+
# ---------------------------------------------------------------------------
info "Checking Python version..."

if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed. Please install Python 3.10 or higher from https://python.org"
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    error "Python 3.10+ is required. Found: Python $PYTHON_VERSION. Please upgrade."
fi

info "Python $PYTHON_VERSION — OK"

# ---------------------------------------------------------------------------
# 2. Create virtual environment and install Python deps
# ---------------------------------------------------------------------------
info "Creating Python virtual environment at backend/venv..."
python3 -m venv backend/venv

info "Activating venv and installing Python dependencies..."
# shellcheck disable=SC1091
source backend/venv/bin/activate
pip install --upgrade pip --quiet
pip install -r backend/requirements.txt

info "Python dependencies installed."

# ---------------------------------------------------------------------------
# 3. Check Node.js 18+
# ---------------------------------------------------------------------------
info "Checking Node.js version..."

if ! command -v node &> /dev/null; then
    error "Node.js is not installed. Please install Node.js 18 or higher from https://nodejs.org"
fi

NODE_VERSION=$(node -e "process.stdout.write(process.version.slice(1))")
NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)

if [ "$NODE_MAJOR" -lt 18 ]; then
    error "Node.js 18+ is required. Found: $NODE_VERSION. Please upgrade."
fi

info "Node.js $NODE_VERSION — OK"

# ---------------------------------------------------------------------------
# 4. Install frontend dependencies
# ---------------------------------------------------------------------------
info "Installing frontend Node.js dependencies..."
cd frontend && npm install --silent && cd ..
info "Frontend dependencies installed."

# ---------------------------------------------------------------------------
# 5. Check Ollama
# ---------------------------------------------------------------------------
if ! command -v ollama &> /dev/null; then
    warn "Ollama is not installed."
    echo ""
    echo "  Install Ollama from: https://ollama.com"
    echo ""
    echo "  On macOS:   brew install ollama"
    echo "  On Linux:   curl -fsSL https://ollama.com/install.sh | sh"
    echo "  On Windows: download the installer from https://ollama.com/download"
    echo ""
    warn "After installing Ollama, run: ollama pull gemma4"
else
    info "Ollama is installed — pulling gemma4 model (this may take several minutes)..."
    ollama pull gemma4
    info "Model gemma4 downloaded and ready."
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║  Setup complete!                                      ║"
echo "║                                                       ║"
echo "║  To run VoiceDoc:                                     ║"
echo "║                                                       ║"
echo "║  Terminal 1:  ollama serve                            ║"
echo "║  Terminal 2:  bash run_backend.sh                     ║"
echo "║  Terminal 3:  bash run_frontend.sh                    ║"
echo "║                                                       ║"
echo "║  Optional: add WHO PDFs to backend/data/ then run:   ║"
echo "║    cd backend && source venv/bin/activate             ║"
echo "║    python ingest_pdfs.py                              ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""


