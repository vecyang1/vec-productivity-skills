#!/bin/bash

# Initialize the folder structure for a new knowledge card project

if [ -z "$1" ]; then
  echo "Usage:   $0 <project_directory>"
  echo "Example: $0 '/Users/vecsatfoxmailcom/Documents/Cowork/Antigravity Cowork/my-knowledge-cards'"
  exit 1
fi

PROJECT_DIR="$1"

echo "Initializing knowledge card project in: $PROJECT_DIR"

# Create core directories
mkdir -p "$PROJECT_DIR/inputs"
mkdir -p "$PROJECT_DIR/planning"
mkdir -p "$PROJECT_DIR/outputs"
mkdir -p "$PROJECT_DIR/reference"

# Create the standard planning document stubs
touch "$PROJECT_DIR/inputs/01-source-content.txt"
touch "$PROJECT_DIR/planning/02-design-prompt.txt"
touch "$PROJECT_DIR/planning/03-design-doc.md"

echo "✅ Project scaffolding complete!"
echo ""
echo "Created directories:"
echo "  📂 inputs/    - Place raw text here"
echo "  📂 planning/  - Design docs and prompts"
echo "  📂 outputs/   - Final generated images"
echo "  📂 reference/ - Style anchors and inspirations"
echo ""
echo "Scaffolding complete in: $PROJECT_DIR"
