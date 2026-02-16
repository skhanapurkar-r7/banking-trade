# PlantUML Diagrams

This folder contains all PlantUML diagram source files for the Trade Store application.

## 📁 Diagram Files

| File | Description | Type |
|------|-------------|------|
| `01-system-architecture.puml` | 3-Tier System Architecture | Component |
| `02-class-diagram.puml` | Domain Model Classes | Class |
| `03-sequence-create-trade-success.puml` | Create Trade Success Flow | Sequence |
| `04-sequence-version-conflict.puml` | Version Conflict Scenario | Sequence |
| `05-sequence-maturity-validation.puml` | Maturity Date Validation | Sequence |
| `06-sequence-get-trades-pagination.puml` | Get Trades with Pagination | Sequence |
| `07-sequence-update-trade.puml` | Update Trade Flow | Sequence |
| `08-sequence-delete-trade.puml` | Delete Trade Flow | Sequence |
| `09-component-diagram.puml` | Application Components | Component |
| `10-deployment-docker.puml` | Docker Deployment | Deployment |
| `11-deployment-multi-environment.puml` | Multi-Environment Setup | Deployment |
| `12-cicd-pipeline-flow.puml` | CI/CD Complete Flow | Activity |
| `13-cicd-detailed-stages.puml` | CI/CD Detailed Stages | Activity |

## 🚀 Generate Diagrams

### Quick Generation

```bash
# From project root
./scripts/generate-diagrams.sh
```

This generates PNG, SVG, and PDF versions in:
- `docs/png/` - PNG images
- `docs/svg/` - SVG images
- `docs/pdf/` - PDF documents

### Manual Generation

```bash
# Generate all as PNG
plantuml -tpng -o ../png docs/diagrams/*.puml

# Generate specific diagram
plantuml -tpng -o ../png docs/diagrams/01-system-architecture.puml

# Generate as SVG
plantuml -tsvg -o ../svg docs/diagrams/*.puml

# Generate as PDF
plantuml -tpdf -o ../pdf docs/diagrams/*.puml
```

## 📊 Output Files

After generation, you'll have:

```
docs/
├── diagrams/                                    # Source files
│   ├── 01-system-architecture.puml
│   ├── 02-class-diagram.puml
│   └── ...
├── png/                                         # PNG images
│   ├── 01-system-architecture.png
│   ├── 02-class-diagram.png
│   └── ...
├── svg/                                         # SVG images
│   ├── 01-system-architecture.svg
│   ├── 02-class-diagram.svg
│   └── ...
└── pdf/                                         # PDF documents
    ├── 01-system-architecture.pdf
    ├── 02-class-diagram.pdf
    └── ...
```

## 🔧 Prerequisites

### Install PlantUML

**macOS:**
```bash
brew install plantuml
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install plantuml
```

**Windows:**
```bash
choco install plantuml
```

**Verify:**
```bash
plantuml -version
```

### VS Code Extension

```bash
code --install-extension jebbs.plantuml
```

Then open any `.puml` file and press `Alt+D` (Windows/Linux) or `Option+D` (macOS) to preview.

## 🌐 Online Viewing

If you don't want to install PlantUML locally:

1. Visit http://www.plantuml.com/plantuml/uml/
2. Copy content from any `.puml` file
3. Paste and view

## 📝 Editing Diagrams

1. Open any `.puml` file in your editor
2. Modify the PlantUML code
3. Regenerate images: `./scripts/generate-diagrams.sh`
4. View updated diagrams in `docs/png/`

## 🎨 Diagram Types

### Component Diagrams
- Show system structure
- Display component relationships
- Illustrate dependencies

### Class Diagrams
- Show domain models
- Display class relationships
- Illustrate inheritance

### Sequence Diagrams
- Show interaction flows
- Display message passing
- Illustrate timing

### Activity Diagrams
- Show process flows
- Display decision points
- Illustrate workflows

### Deployment Diagrams
- Show physical architecture
- Display deployment nodes
- Illustrate infrastructure

## 📚 Resources

- [PlantUML Documentation](https://plantuml.com/)
- [PlantUML Cheat Sheet](https://plantuml.com/guide)
- [Sequence Diagram Guide](https://plantuml.com/sequence-diagram)
- [Class Diagram Guide](https://plantuml.com/class-diagram)
- [Component Diagram Guide](https://plantuml.com/component-diagram)

---

**Last Updated**: 2024-02-10
**Total Diagrams**: 13
