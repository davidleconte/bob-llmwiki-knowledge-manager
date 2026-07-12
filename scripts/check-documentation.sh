#!/bin/bash
set -e

# check-documentation.sh
# Checks documentation coverage across the codebase
# Usage: ./scripts/check-documentation.sh [output-file]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default output location
OUTPUT_FILE="${1:-docs/knowledge-base/research/doc-coverage-$(date +%Y-%m-%d).md}"

echo -e "${GREEN}📚 Checking Documentation Coverage...${NC}"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Start generating report
cat > "$OUTPUT_FILE" << EOF
# Documentation Coverage Report

**Generated:** $(date +"%Y-%m-%d %H:%M:%S")  
**Tool:** check-documentation.sh  
**Version:** 1.0

---

## Executive Summary

EOF

# Function to check README completeness
check_readme() {
    echo -e "${BLUE}Checking README...${NC}"
    
    echo "### README Analysis" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if [ -f "README.md" ]; then
        echo "**Status:** ✅ README.md exists" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        # Check for essential sections
        echo "#### Essential Sections" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "| Section | Present |" >> "$OUTPUT_FILE"
        echo "|---------|---------|" >> "$OUTPUT_FILE"
        
        grep -qi "# \|## " README.md && echo "| Headings | ✅ |" >> "$OUTPUT_FILE" || echo "| Headings | ❌ |" >> "$OUTPUT_FILE"
        grep -qi "install\|setup" README.md && echo "| Installation | ✅ |" >> "$OUTPUT_FILE" || echo "| Installation | ❌ |" >> "$OUTPUT_FILE"
        grep -qi "usage\|getting started\|quick start" README.md && echo "| Usage | ✅ |" >> "$OUTPUT_FILE" || echo "| Usage | ❌ |" >> "$OUTPUT_FILE"
        grep -qi "example\|demo" README.md && echo "| Examples | ✅ |" >> "$OUTPUT_FILE" || echo "| Examples | ❌ |" >> "$OUTPUT_FILE"
        grep -qi "contribut" README.md && echo "| Contributing | ✅ |" >> "$OUTPUT_FILE" || echo "| Contributing | ❌ |" >> "$OUTPUT_FILE"
        grep -qi "license" README.md && echo "| License | ✅ |" >> "$OUTPUT_FILE" || echo "| License | ❌ |" >> "$OUTPUT_FILE"
        
        echo "" >> "$OUTPUT_FILE"
        
        # README length
        LINES=$(wc -l < README.md | tr -d ' ')
        echo "**Length:** $LINES lines" >> "$OUTPUT_FILE"
        
        if [ $LINES -lt 50 ]; then
            echo "⚠️  README is quite short - consider adding more detail" >> "$OUTPUT_FILE"
        elif [ $LINES -gt 500 ]; then
            echo "⚠️  README is very long - consider splitting into separate docs" >> "$OUTPUT_FILE"
        else
            echo "✅ README length is appropriate" >> "$OUTPUT_FILE"
        fi
        
    else
        echo "**Status:** ❌ README.md missing" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "⚠️  **Critical:** Every project should have a README.md" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to check Python documentation
check_python_docs() {
    if [ $(find . -name "*.py" -not -path '*/venv/*' -not -path '*/__pycache__/*' | wc -l) -eq 0 ]; then
        return
    fi
    
    echo -e "${BLUE}Checking Python documentation...${NC}"
    
    echo "### Python Documentation" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Count Python files
    TOTAL_PY=$(find . -name "*.py" -not -path '*/venv/*' -not -path '*/__pycache__/*' -not -path '*/build/*' -not -path '*/dist/*' | wc -l | tr -d ' ')
    echo "**Total Python Files:** $TOTAL_PY" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Check for docstrings
    echo "#### Docstring Coverage" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if command -v interrogate &> /dev/null; then
        echo '```' >> "$OUTPUT_FILE"
        interrogate . --exclude venv --exclude __pycache__ --exclude build --exclude dist 2>/dev/null | tail -15 >> "$OUTPUT_FILE" || echo "interrogate failed" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
    else
        # Manual check
        FILES_WITH_DOCSTRINGS=$(find . -name "*.py" -not -path '*/venv/*' -not -path '*/__pycache__/*' -exec grep -l '"""' {} \; 2>/dev/null | wc -l | tr -d ' ')
        PERCENT=$(awk "BEGIN {if($TOTAL_PY>0) printf \"%.1f\", ($FILES_WITH_DOCSTRINGS/$TOTAL_PY)*100; else print \"0\"}")
        
        echo "Files with docstrings: $FILES_WITH_DOCSTRINGS / $TOTAL_PY ($PERCENT%)" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "*Install interrogate for detailed analysis: \`pip install interrogate\`*" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    
    # Check for type hints
    echo "#### Type Hints" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if command -v mypy &> /dev/null; then
        echo '```' >> "$OUTPUT_FILE"
        mypy . --ignore-missing-imports --no-error-summary 2>/dev/null | head -20 >> "$OUTPUT_FILE" || echo "mypy check completed" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
    else
        FILES_WITH_HINTS=$(find . -name "*.py" -not -path '*/venv/*' -not -path '*/__pycache__/*' -exec grep -l '->.*:' {} \; 2>/dev/null | wc -l | tr -d ' ')
        PERCENT=$(awk "BEGIN {if($TOTAL_PY>0) printf \"%.1f\", ($FILES_WITH_HINTS/$TOTAL_PY)*100; else print \"0\"}")
        
        echo "Files with type hints: $FILES_WITH_HINTS / $TOTAL_PY ($PERCENT%)" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "*Install mypy for type checking: \`pip install mypy\`*" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to check JavaScript/TypeScript documentation
check_javascript_docs() {
    if [ ! -f "package.json" ]; then
        return
    fi
    
    echo -e "${BLUE}Checking JavaScript/TypeScript documentation...${NC}"
    
    echo "### JavaScript/TypeScript Documentation" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Count JS/TS files
    TOTAL_JS=$(find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -not -path '*/node_modules/*' | wc -l | tr -d ' ')
    echo "**Total JS/TS Files:** $TOTAL_JS" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Check for JSDoc comments
    echo "#### JSDoc Coverage" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    FILES_WITH_JSDOC=$(find . \( -name "*.js" -o -name "*.ts" \) -not -path '*/node_modules/*' -exec grep -l '/\*\*' {} \; 2>/dev/null | wc -l | tr -d ' ')
    PERCENT=$(awk "BEGIN {if($TOTAL_JS>0) printf \"%.1f\", ($FILES_WITH_JSDOC/$TOTAL_JS)*100; else print \"0\"}")
    
    echo "Files with JSDoc: $FILES_WITH_JSDOC / $TOTAL_JS ($PERCENT%)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Check for TypeScript
    if [ $(find . -name "*.ts" -o -name "*.tsx" -not -path '*/node_modules/*' | wc -l) -gt 0 ]; then
        echo "✅ TypeScript provides type documentation" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to check inline comments
check_inline_comments() {
    echo -e "${BLUE}Checking inline comments...${NC}"
    
    echo "### Inline Comments" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Python comments
    if [ $(find . -name "*.py" -not -path '*/venv/*' -not -path '*/__pycache__/*' | wc -l) -gt 0 ]; then
        TOTAL_PY_LINES=$(find . -name "*.py" -not -path '*/venv/*' -not -path '*/__pycache__/*' -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
        PY_COMMENT_LINES=$(find . -name "*.py" -not -path '*/venv/*' -not -path '*/__pycache__/*' -exec grep -h '^\s*#' {} \; 2>/dev/null | wc -l | tr -d ' ')
        PY_PERCENT=$(awk "BEGIN {if($TOTAL_PY_LINES>0) printf \"%.1f\", ($PY_COMMENT_LINES/$TOTAL_PY_LINES)*100; else print \"0\"}")
        
        echo "**Python:** $PY_COMMENT_LINES comment lines / $TOTAL_PY_LINES total lines ($PY_PERCENT%)" >> "$OUTPUT_FILE"
    fi
    
    # JavaScript comments
    if [ -f "package.json" ]; then
        TOTAL_JS_LINES=$(find . \( -name "*.js" -o -name "*.ts" \) -not -path '*/node_modules/*' -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
        JS_COMMENT_LINES=$(find . \( -name "*.js" -o -name "*.ts" \) -not -path '*/node_modules/*' -exec grep -h '^\s*//' {} \; 2>/dev/null | wc -l | tr -d ' ')
        JS_PERCENT=$(awk "BEGIN {if($TOTAL_JS_LINES>0) printf \"%.1f\", ($JS_COMMENT_LINES/$TOTAL_JS_LINES)*100; else print \"0\"}")
        
        echo "**JavaScript/TypeScript:** $JS_COMMENT_LINES comment lines / $TOTAL_JS_LINES total lines ($JS_PERCENT%)" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "**Recommended:** 10-20% comment ratio for good documentation" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to check for documentation directory
check_docs_directory() {
    echo -e "${BLUE}Checking documentation directory...${NC}"
    
    echo "### Documentation Directory" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if [ -d "docs" ] || [ -d "doc" ] || [ -d "documentation" ]; then
        echo "**Status:** ✅ Documentation directory exists" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        # Count markdown files
        MD_COUNT=$(find docs doc documentation -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        echo "**Markdown Files:** $MD_COUNT" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        # List main docs
        echo "#### Documentation Files" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        find docs doc documentation -maxdepth 2 -name "*.md" 2>/dev/null | head -20 | while read file; do
            echo "- \`$file\`" >> "$OUTPUT_FILE"
        done
    else
        echo "**Status:** ❌ No documentation directory found" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "⚠️  Consider creating a \`docs/\` directory for project documentation" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to check API documentation
check_api_docs() {
    echo -e "${BLUE}Checking API documentation...${NC}"
    
    echo "### API Documentation" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Check for common API doc files
    API_DOCS_FOUND=false
    
    [ -f "API.md" ] && echo "- ✅ API.md found" >> "$OUTPUT_FILE" && API_DOCS_FOUND=true
    [ -f "docs/API.md" ] && echo "- ✅ docs/API.md found" >> "$OUTPUT_FILE" && API_DOCS_FOUND=true
    [ -f "docs/api/README.md" ] && echo "- ✅ docs/api/README.md found" >> "$OUTPUT_FILE" && API_DOCS_FOUND=true
    [ -d "docs/api" ] && echo "- ✅ docs/api/ directory found" >> "$OUTPUT_FILE" && API_DOCS_FOUND=true
    
    # Check for OpenAPI/Swagger
    [ -f "openapi.yaml" ] || [ -f "openapi.yml" ] || [ -f "swagger.yaml" ] || [ -f "swagger.yml" ] && echo "- ✅ OpenAPI/Swagger spec found" >> "$OUTPUT_FILE" && API_DOCS_FOUND=true
    
    if [ "$API_DOCS_FOUND" = false ]; then
        echo "❌ No API documentation found" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "⚠️  If this project exposes an API, consider adding API documentation" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to generate summary
generate_summary() {
    echo "## Summary & Recommendations" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Documentation Quality Score" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    SCORE=0
    [ -f "README.md" ] && SCORE=$((SCORE + 20))
    [ -d "docs" ] || [ -d "doc" ] && SCORE=$((SCORE + 15))
    [ -f "CONTRIBUTING.md" ] && SCORE=$((SCORE + 10))
    [ -f "LICENSE" ] && SCORE=$((SCORE + 10))
    [ $(find . -name "*.py" -not -path '*/venv/*' -exec grep -l '"""' {} \; 2>/dev/null | wc -l) -gt 0 ] && SCORE=$((SCORE + 15))
    [ -f "API.md" ] || [ -f "docs/API.md" ] && SCORE=$((SCORE + 15))
    [ -f "CHANGELOG.md" ] && SCORE=$((SCORE + 10))
    [ -f ".github/PULL_REQUEST_TEMPLATE.md" ] && SCORE=$((SCORE + 5))
    
    echo "**Score:** $SCORE / 100" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if [ $SCORE -ge 80 ]; then
        echo "🟢 **Excellent** - Well documented project" >> "$OUTPUT_FILE"
    elif [ $SCORE -ge 60 ]; then
        echo "🟡 **Good** - Adequate documentation with room for improvement" >> "$OUTPUT_FILE"
    elif [ $SCORE -ge 40 ]; then
        echo "🟠 **Fair** - Basic documentation present, needs enhancement" >> "$OUTPUT_FILE"
    else
        echo "🔴 **Poor** - Insufficient documentation" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Recommendations" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "1. **README:** Ensure comprehensive README with all essential sections" >> "$OUTPUT_FILE"
    echo "2. **Code Comments:** Maintain 10-20% comment ratio" >> "$OUTPUT_FILE"
    echo "3. **API Docs:** Document all public APIs and endpoints" >> "$OUTPUT_FILE"
    echo "4. **Docstrings:** Add docstrings to all public functions/classes" >> "$OUTPUT_FILE"
    echo "5. **Type Hints:** Use type hints for better code documentation" >> "$OUTPUT_FILE"
    echo "6. **Examples:** Include usage examples in documentation" >> "$OUTPUT_FILE"
    echo "7. **Changelog:** Maintain CHANGELOG.md for version history" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "*Generated by check-documentation.sh - Part of Bob Shell Knowledge Manager*" >> "$OUTPUT_FILE"
}

# Run all checks
check_readme
check_python_docs
check_javascript_docs
check_inline_comments
check_docs_directory
check_api_docs
generate_summary

echo -e "${GREEN}✅ Documentation coverage check complete!${NC}"
echo -e "${YELLOW}📄 Report saved to: $OUTPUT_FILE${NC}"
echo ""
echo "Next steps:"
echo "1. Review documentation coverage report"
echo "2. Address documentation gaps"
echo "3. Run generate-analysis-report.sh to consolidate all findings"
