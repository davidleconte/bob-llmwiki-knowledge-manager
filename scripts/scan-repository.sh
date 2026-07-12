#!/bin/bash
set -e

# scan-repository.sh
# Generates comprehensive repository overview
# Usage: ./scripts/scan-repository.sh [output-file]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default output location
OUTPUT_FILE="${1:-docs/knowledge-base/research/repo-scan-$(date +%Y-%m-%d).md}"

echo -e "${GREEN}📊 Scanning Repository...${NC}"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Start generating report
cat > "$OUTPUT_FILE" << 'EOF'
# Repository Scan Report

**Generated:** $(date +"%Y-%m-%d %H:%M:%S")  
**Tool:** scan-repository.sh  
**Version:** 1.0

---

## Executive Summary

EOF

# Get repository name
REPO_NAME=$(basename "$(pwd)")
echo "**Repository:** $REPO_NAME" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Count files by type
echo "### File Statistics" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| Type | Count | Percentage |" >> "$OUTPUT_FILE"
echo "|------|-------|------------|" >> "$OUTPUT_FILE"

TOTAL_FILES=$(find . -type f -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/venv/*' -not -path '*/__pycache__/*' -not -path '*/dist/*' -not -path '*/build/*' | wc -l | tr -d ' ')

# Count by extension
for ext in py js ts jsx tsx java go rs c cpp h md txt json yaml yml xml html css scss; do
    COUNT=$(find . -type f -name "*.$ext" -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/venv/*' -not -path '*/__pycache__/*' -not -path '*/dist/*' -not -path '*/build/*' 2>/dev/null | wc -l | tr -d ' ')
    if [ "$COUNT" -gt 0 ]; then
        PERCENT=$(awk "BEGIN {printf \"%.1f\", ($COUNT/$TOTAL_FILES)*100}")
        echo "| .$ext | $COUNT | $PERCENT% |" >> "$OUTPUT_FILE"
    fi
done

echo "" >> "$OUTPUT_FILE"
echo "**Total Files:** $TOTAL_FILES" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Directory structure
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Directory Structure" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"

# Generate tree (limit depth to 3)
if command -v tree &> /dev/null; then
    tree -L 3 -I 'node_modules|venv|__pycache__|.git|dist|build|.pytest_cache' >> "$OUTPUT_FILE"
else
    # Fallback if tree is not available
    find . -type d -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/venv/*' -not -path '*/__pycache__/*' -not -path '*/dist/*' -not -path '*/build/*' | head -50 | sort >> "$OUTPUT_FILE"
fi

echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Key files identification
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Key Files Identified" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Check for common key files
KEY_FILES=(
    "README.md:Project documentation"
    "CONTRIBUTING.md:Contribution guidelines"
    "LICENSE:License information"
    "package.json:Node.js dependencies"
    "requirements.txt:Python dependencies"
    "Cargo.toml:Rust dependencies"
    "go.mod:Go dependencies"
    "pom.xml:Maven dependencies"
    "build.gradle:Gradle dependencies"
    "Makefile:Build automation"
    "Dockerfile:Container configuration"
    "docker-compose.yml:Multi-container setup"
    ".gitignore:Git ignore patterns"
    ".env.example:Environment variables template"
    "tsconfig.json:TypeScript configuration"
    "pytest.ini:Pytest configuration"
    "setup.py:Python package setup"
    "main.py:Python entry point"
    "index.js:JavaScript entry point"
    "main.go:Go entry point"
    "main.rs:Rust entry point"
)

echo "| File | Purpose | Exists |" >> "$OUTPUT_FILE"
echo "|------|---------|--------|" >> "$OUTPUT_FILE"

for item in "${KEY_FILES[@]}"; do
    FILE="${item%%:*}"
    DESC="${item#*:}"
    if [ -f "$FILE" ]; then
        echo "| $FILE | $DESC | ✅ |" >> "$OUTPUT_FILE"
    else
        echo "| $FILE | $DESC | ❌ |" >> "$OUTPUT_FILE"
    fi
done

echo "" >> "$OUTPUT_FILE"

# Technology stack detection
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Technology Stack" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Detect languages
echo "### Languages Detected" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

LANGS=()
[ $(find . -name "*.py" -not -path '*/\.*' -not -path '*/venv/*' | head -1 | wc -l) -gt 0 ] && LANGS+=("Python")
[ $(find . -name "*.js" -not -path '*/\.*' -not -path '*/node_modules/*' | head -1 | wc -l) -gt 0 ] && LANGS+=("JavaScript")
[ $(find . -name "*.ts" -not -path '*/\.*' -not -path '*/node_modules/*' | head -1 | wc -l) -gt 0 ] && LANGS+=("TypeScript")
[ $(find . -name "*.java" -not -path '*/\.*' | head -1 | wc -l) -gt 0 ] && LANGS+=("Java")
[ $(find . -name "*.go" -not -path '*/\.*' | head -1 | wc -l) -gt 0 ] && LANGS+=("Go")
[ $(find . -name "*.rs" -not -path '*/\.*' | head -1 | wc -l) -gt 0 ] && LANGS+=("Rust")
[ $(find . -name "*.c" -o -name "*.cpp" -not -path '*/\.*' | head -1 | wc -l) -gt 0 ] && LANGS+=("C/C++")

for lang in "${LANGS[@]}"; do
    echo "- $lang" >> "$OUTPUT_FILE"
done

echo "" >> "$OUTPUT_FILE"

# Detect frameworks
echo "### Frameworks/Tools Detected" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

[ -f "package.json" ] && grep -q "react" package.json 2>/dev/null && echo "- React" >> "$OUTPUT_FILE"
[ -f "package.json" ] && grep -q "vue" package.json 2>/dev/null && echo "- Vue.js" >> "$OUTPUT_FILE"
[ -f "package.json" ] && grep -q "angular" package.json 2>/dev/null && echo "- Angular" >> "$OUTPUT_FILE"
[ -f "package.json" ] && grep -q "express" package.json 2>/dev/null && echo "- Express.js" >> "$OUTPUT_FILE"
[ -f "requirements.txt" ] && grep -q "django" requirements.txt 2>/dev/null && echo "- Django" >> "$OUTPUT_FILE"
[ -f "requirements.txt" ] && grep -q "flask" requirements.txt 2>/dev/null && echo "- Flask" >> "$OUTPUT_FILE"
[ -f "requirements.txt" ] && grep -q "fastapi" requirements.txt 2>/dev/null && echo "- FastAPI" >> "$OUTPUT_FILE"
[ -f "go.mod" ] && grep -q "gin" go.mod 2>/dev/null && echo "- Gin (Go)" >> "$OUTPUT_FILE"
[ -f "Cargo.toml" ] && grep -q "actix" Cargo.toml 2>/dev/null && echo "- Actix (Rust)" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"

# Entry points
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Entry Points" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

ENTRY_POINTS=()
[ -f "main.py" ] && ENTRY_POINTS+=("main.py")
[ -f "app.py" ] && ENTRY_POINTS+=("app.py")
[ -f "index.js" ] && ENTRY_POINTS+=("index.js")
[ -f "main.js" ] && ENTRY_POINTS+=("main.js")
[ -f "server.js" ] && ENTRY_POINTS+=("server.js")
[ -f "main.go" ] && ENTRY_POINTS+=("main.go")
[ -f "main.rs" ] && ENTRY_POINTS+=("main.rs")
[ -f "src/main.rs" ] && ENTRY_POINTS+=("src/main.rs")

if [ ${#ENTRY_POINTS[@]} -gt 0 ]; then
    for entry in "${ENTRY_POINTS[@]}"; do
        echo "- \`$entry\`" >> "$OUTPUT_FILE"
    done
else
    echo "*No standard entry points detected*" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"

# Test directories
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Testing Infrastructure" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

TEST_DIRS=()
[ -d "tests" ] && TEST_DIRS+=("tests/")
[ -d "test" ] && TEST_DIRS+=("test/")
[ -d "__tests__" ] && TEST_DIRS+=("__tests__/")
[ -d "spec" ] && TEST_DIRS+=("spec/")

if [ ${#TEST_DIRS[@]} -gt 0 ]; then
    echo "**Test Directories Found:**" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    for dir in "${TEST_DIRS[@]}"; do
        TEST_COUNT=$(find "$dir" -type f \( -name "test_*.py" -o -name "*_test.py" -o -name "*.test.js" -o -name "*.spec.js" -o -name "*_test.go" \) 2>/dev/null | wc -l | tr -d ' ')
        echo "- \`$dir\` - $TEST_COUNT test files" >> "$OUTPUT_FILE"
    done
else
    echo "*No standard test directories found*" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"

# Configuration files
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Configuration Files" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

CONFIG_FILES=$(find . -maxdepth 2 -type f \( -name "*.config.js" -o -name "*.config.ts" -o -name "*.yml" -o -name "*.yaml" -o -name "*.toml" -o -name "*.ini" \) -not -path '*/\.*' -not -path '*/node_modules/*' 2>/dev/null)

if [ -n "$CONFIG_FILES" ]; then
    echo "$CONFIG_FILES" | while read -r file; do
        echo "- \`$file\`" >> "$OUTPUT_FILE"
    done
else
    echo "*No configuration files found in root/first level*" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"

# Summary
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Scan Summary" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "- **Total Files:** $TOTAL_FILES" >> "$OUTPUT_FILE"
echo "- **Languages:** ${#LANGS[@]}" >> "$OUTPUT_FILE"
echo "- **Entry Points:** ${#ENTRY_POINTS[@]}" >> "$OUTPUT_FILE"
echo "- **Test Directories:** ${#TEST_DIRS[@]}" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "*Generated by scan-repository.sh - Part of Bob Shell Knowledge Manager*" >> "$OUTPUT_FILE"

echo -e "${GREEN}✅ Repository scan complete!${NC}"
echo -e "${YELLOW}📄 Report saved to: $OUTPUT_FILE${NC}"
echo ""
echo "Next steps:"
echo "1. Review the scan report"
echo "2. Run analyze-dependencies.sh for dependency analysis"
echo "3. Run collect-metrics.sh for code metrics"
