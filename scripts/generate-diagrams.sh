#!/bin/bash

# Script to generate PlantUML diagrams in multiple formats

set -e

echo "🎨 Generating PlantUML Diagrams..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if plantuml is installed
if ! command -v plantuml &> /dev/null; then
    echo "❌ PlantUML is not installed!"
    echo ""
    echo "Install with:"
    echo "  macOS:   brew install plantuml"
    echo "  Linux:   sudo apt install plantuml"
    echo "  Windows: choco install plantuml"
    echo ""
    echo "Or use Docker:"
    echo "  docker run -d -p 8080:8080 plantuml/plantuml-server:jetty"
    exit 1
fi

echo "✓ PlantUML found: $(plantuml -version | head -n 1)"
echo ""

# Create output directories
echo "📁 Creating output directories..."
mkdir -p docs/png
mkdir -p docs/svg
mkdir -p docs/pdf
echo "✓ Directories created"
echo ""

# Generate PNG diagrams
echo "🖼️  Generating PNG diagrams..."
plantuml -tpng -o ../png docs/diagrams/*.puml
PNG_COUNT=$(ls -1 docs/png/*.png 2>/dev/null | wc -l)
echo "✓ Generated $PNG_COUNT PNG files in docs/png/"
echo ""

# Generate SVG diagrams
echo "🎨 Generating SVG diagrams..."
plantuml -tsvg -o ../svg docs/diagrams/*.puml
SVG_COUNT=$(ls -1 docs/svg/*.svg 2>/dev/null | wc -l)
echo "✓ Generated $SVG_COUNT SVG files in docs/svg/"
echo ""

# Generate PDF diagrams
echo "📄 Generating PDF diagrams..."
plantuml -tpdf -o ../pdf docs/diagrams/*.puml
PDF_COUNT=$(ls -1 docs/pdf/*.pdf 2>/dev/null | wc -l)
echo "✓ Generated $PDF_COUNT PDF files in docs/pdf/"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All diagrams generated successfully!"
echo ""
echo "Generated files:"
echo ""
ls -1 docs/png/*.png | sed 's/^/  /'
echo ""
echo "Output locations:"
echo "  PNG: docs/png/"
echo "  SVG: docs/svg/"
echo "  PDF: docs/pdf/"
echo ""
echo "View diagrams:"
echo "  open docs/png/  # macOS"
echo "  xdg-open docs/png/  # Linux"
