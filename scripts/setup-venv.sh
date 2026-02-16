#!/bin/bash

set -e

echo "🚀 Setting up Backend Environment..."

# Use Python 3.11
PYTHON_CMD="python3.11"

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python 3.11 is not found."
    echo "Please ensure Python 3.11 is installed and available in PATH."
    exit 1
fi

VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
echo "✓ Found Python $VERSION"

# Remove old venv if it exists
if [ -d "venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "📦 Creating virtual environment with $PYTHON_CMD..."
$PYTHON_CMD -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies from pyproject.toml
echo "📦 Installing backend dependencies..."
pip install poetry
poetry install

# Create .env directory and file if it doesn't exist
if [ ! -d ".env" ]; then
    mkdir -p .env
fi

if [ ! -f ".env/.env" ]; then
    echo "📝 Creating .env file..."
    cat > .env/.env << EOF
DATABASE_URL=sqlite:///./src/db/trades.db
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EOF
    echo "✓ Created .env file"
fi

# Create db directory if it doesn't exist
if [ ! -d "src/db" ]; then
    mkdir -p src/db
    echo "✓ Created db directory"
fi

echo "✅ Backend setup complete!"
echo ""
echo "Virtual environment is now active!"
echo ""
echo "To activate the virtual environment in a new terminal, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the backend server, run:"
echo "  uvicorn src.app.main:app --reload"
echo ""
echo "To run tests, run:"
echo "  pytest"
