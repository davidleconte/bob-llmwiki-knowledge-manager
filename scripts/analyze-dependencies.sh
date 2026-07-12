#!/bin/bash
set -e

# analyze-dependencies.sh
# Analyzes project dependencies across multiple package managers
# Usage: ./scripts/analyze-dependencies.sh [output-file]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default output location
OUTPUT_FILE="${1:-docs/knowledge-base/concepts/dependency-analysis.md}"

echo -e "${GREEN}📦 Analyzing Dependencies...${NC}"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Start generating report
cat > "$OUTPUT_FILE" << EOF
# Dependency Analysis Report

**Generated:** $(date +"%Y-%m-%d %H:%M:%S")  
**Tool:** analyze-dependencies.sh  
**Version:** 1.0

---

## Executive Summary

EOF

# Function to analyze package.json (Node.js)
analyze_nodejs() {
    if [ ! -f "package.json" ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing Node.js dependencies...${NC}"
    
    echo "### Node.js Dependencies (package.json)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Count dependencies
    DEPS=$(grep -c '"' package.json 2>/dev/null || echo "0")
    PROD_DEPS=$(jq -r '.dependencies | length' package.json 2>/dev/null || echo "0")
    DEV_DEPS=$(jq -r '.devDependencies | length' package.json 2>/dev/null || echo "0")
    
    echo "**Summary:**" >> "$OUTPUT_FILE"
    echo "- Production dependencies: $PROD_DEPS" >> "$OUTPUT_FILE"
    echo "- Development dependencies: $DEV_DEPS" >> "$OUTPUT_FILE"
    echo "- Total: $((PROD_DEPS + DEV_DEPS))" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # List production dependencies
    if [ "$PROD_DEPS" -gt 0 ]; then
        echo "#### Production Dependencies" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "| Package | Version |" >> "$OUTPUT_FILE"
        echo "|---------|---------|" >> "$OUTPUT_FILE"
        
        if command -v jq &> /dev/null; then
            jq -r '.dependencies | to_entries[] | "| \(.key) | \(.value) |"' package.json >> "$OUTPUT_FILE"
        else
            echo "*jq not installed - cannot parse dependencies*" >> "$OUTPUT_FILE"
        fi
        echo "" >> "$OUTPUT_FILE"
    fi
    
    # List dev dependencies
    if [ "$DEV_DEPS" -gt 0 ]; then
        echo "#### Development Dependencies" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "| Package | Version |" >> "$OUTPUT_FILE"
        echo "|---------|---------|" >> "$OUTPUT_FILE"
        
        if command -v jq &> /dev/null; then
            jq -r '.devDependencies | to_entries[] | "| \(.key) | \(.value) |"' package.json >> "$OUTPUT_FILE"
        else
            echo "*jq not installed - cannot parse dependencies*" >> "$OUTPUT_FILE"
        fi
        echo "" >> "$OUTPUT_FILE"
    fi
    
    # Security audit
    echo "#### Security Audit" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if command -v npm &> /dev/null && [ -f "package-lock.json" ]; then
        echo '```' >> "$OUTPUT_FILE"
        npm audit --json 2>/dev/null | jq -r '.metadata | "Vulnerabilities: \(.vulnerabilities.total)\nCritical: \(.vulnerabilities.critical)\nHigh: \(.vulnerabilities.high)\nModerate: \(.vulnerabilities.moderate)\nLow: \(.vulnerabilities.low)"' >> "$OUTPUT_FILE" 2>/dev/null || echo "npm audit failed or no vulnerabilities found" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
    else
        echo "*npm not available or package-lock.json missing*" >> "$OUTPUT_FILE"
    fi
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze requirements.txt (Python)
analyze_python() {
    if [ ! -f "requirements.txt" ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing Python dependencies...${NC}"
    
    echo "### Python Dependencies (requirements.txt)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Count dependencies
    DEPS=$(grep -v '^#' requirements.txt | grep -v '^$' | wc -l | tr -d ' ')
    
    echo "**Summary:**" >> "$OUTPUT_FILE"
    echo "- Total dependencies: $DEPS" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # List dependencies
    echo "#### Dependencies" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| Package | Version Constraint |" >> "$OUTPUT_FILE"
    echo "|---------|-------------------|" >> "$OUTPUT_FILE"
    
    grep -v '^#' requirements.txt | grep -v '^$' | while IFS= read -r line; do
        if [[ $line == *"=="* ]]; then
            PKG="${line%%==*}"
            VER="${line#*==}"
            echo "| $PKG | ==$VER |" >> "$OUTPUT_FILE"
        elif [[ $line == *">="* ]]; then
            PKG="${line%%>=*}"
            VER="${line#*>=}"
            echo "| $PKG | >=$VER |" >> "$OUTPUT_FILE"
        else
            echo "| $line | (any) |" >> "$OUTPUT_FILE"
        fi
    done
    
    echo "" >> "$OUTPUT_FILE"
    
    # Security audit
    echo "#### Security Audit" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if command -v safety &> /dev/null; then
        echo '```' >> "$OUTPUT_FILE"
        safety check --json 2>/dev/null | jq -r '.[] | "[\(.severity)] \(.package) \(.installed_version): \(.vulnerability)"' >> "$OUTPUT_FILE" 2>/dev/null || echo "No vulnerabilities found or safety check failed" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
    elif command -v pip-audit &> /dev/null; then
        echo '```' >> "$OUTPUT_FILE"
        pip-audit --format json 2>/dev/null | jq -r '.dependencies[] | "[\(.vulns[0].severity)] \(.name) \(.version): \(.vulns[0].description)"' >> "$OUTPUT_FILE" 2>/dev/null || echo "No vulnerabilities found or pip-audit failed" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
    else
        echo "*safety or pip-audit not installed - cannot check for vulnerabilities*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "Install with: \`pip install safety\` or \`pip install pip-audit\`" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze go.mod (Go)
analyze_go() {
    if [ ! -f "go.mod" ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing Go dependencies...${NC}"
    
    echo "### Go Dependencies (go.mod)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Count dependencies
    DEPS=$(grep -c 'require' go.mod 2>/dev/null || echo "0")
    
    echo "**Summary:**" >> "$OUTPUT_FILE"
    echo "- Total dependencies: $DEPS" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # List dependencies
    echo "#### Dependencies" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    grep 'require' go.mod | head -20 >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze Cargo.toml (Rust)
analyze_rust() {
    if [ ! -f "Cargo.toml" ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing Rust dependencies...${NC}"
    
    echo "### Rust Dependencies (Cargo.toml)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Count dependencies
    DEPS=$(grep -c '=' Cargo.toml 2>/dev/null || echo "0")
    
    echo "**Summary:**" >> "$OUTPUT_FILE"
    echo "- Total dependencies: $DEPS" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # List dependencies
    echo "#### Dependencies" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo '```toml' >> "$OUTPUT_FILE"
    sed -n '/\[dependencies\]/,/\[/p' Cargo.toml | grep -v '^\[' >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze pom.xml (Maven/Java)
analyze_maven() {
    if [ ! -f "pom.xml" ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing Maven dependencies...${NC}"
    
    echo "### Maven Dependencies (pom.xml)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Count dependencies
    DEPS=$(grep -c '<dependency>' pom.xml 2>/dev/null || echo "0")
    
    echo "**Summary:**" >> "$OUTPUT_FILE"
    echo "- Total dependencies: $DEPS" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "#### Dependencies" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "*See pom.xml for full dependency list*" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze build.gradle (Gradle)
analyze_gradle() {
    if [ ! -f "build.gradle" ] && [ ! -f "build.gradle.kts" ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing Gradle dependencies...${NC}"
    
    echo "### Gradle Dependencies" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    GRADLE_FILE="build.gradle"
    [ -f "build.gradle.kts" ] && GRADLE_FILE="build.gradle.kts"
    
    # Count dependencies
    DEPS=$(grep -c 'implementation\|api\|compile' "$GRADLE_FILE" 2>/dev/null || echo "0")
    
    echo "**Summary:**" >> "$OUTPUT_FILE"
    echo "- Total dependencies: $DEPS" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "#### Dependencies" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    grep 'implementation\|api\|compile' "$GRADLE_FILE" | head -20 >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Run all analyzers
analyze_nodejs
analyze_python
analyze_go
analyze_rust
analyze_maven
analyze_gradle

# Summary
echo "## Overall Summary" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

FOUND_DEPS=false
[ -f "package.json" ] && echo "- ✅ Node.js dependencies found" >> "$OUTPUT_FILE" && FOUND_DEPS=true
[ -f "requirements.txt" ] && echo "- ✅ Python dependencies found" >> "$OUTPUT_FILE" && FOUND_DEPS=true
[ -f "go.mod" ] && echo "- ✅ Go dependencies found" >> "$OUTPUT_FILE" && FOUND_DEPS=true
[ -f "Cargo.toml" ] && echo "- ✅ Rust dependencies found" >> "$OUTPUT_FILE" && FOUND_DEPS=true
[ -f "pom.xml" ] && echo "- ✅ Maven dependencies found" >> "$OUTPUT_FILE" && FOUND_DEPS=true
[ -f "build.gradle" ] || [ -f "build.gradle.kts" ] && echo "- ✅ Gradle dependencies found" >> "$OUTPUT_FILE" && FOUND_DEPS=true

if [ "$FOUND_DEPS" = false ]; then
    echo "- ❌ No dependency files found" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"
echo "## Recommendations" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "1. **Security:** Run security audits regularly" >> "$OUTPUT_FILE"
echo "2. **Updates:** Keep dependencies up to date" >> "$OUTPUT_FILE"
echo "3. **Audit:** Review dependency licenses for compliance" >> "$OUTPUT_FILE"
echo "4. **Minimize:** Remove unused dependencies" >> "$OUTPUT_FILE"
echo "5. **Lock:** Use lock files (package-lock.json, requirements.txt with ==)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "*Generated by analyze-dependencies.sh - Part of Bob Shell Knowledge Manager*" >> "$OUTPUT_FILE"

echo -e "${GREEN}✅ Dependency analysis complete!${NC}"
echo -e "${YELLOW}📄 Report saved to: $OUTPUT_FILE${NC}"
echo ""
echo "Next steps:"
echo "1. Review dependency report"
echo "2. Address any security vulnerabilities"
echo "3. Run collect-metrics.sh for code quality metrics"
