#!/bin/bash
set -e

# collect-metrics.sh
# Collects code quality metrics using available tools
# Usage: ./scripts/collect-metrics.sh [output-file]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default output location
OUTPUT_FILE="${1:-docs/knowledge-base/research/code-metrics-$(date +%Y-%m-%d).md}"

echo -e "${GREEN}📊 Collecting Code Metrics...${NC}"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Start generating report
cat > "$OUTPUT_FILE" << EOF
# Code Metrics Report

**Generated:** $(date +"%Y-%m-%d %H:%M:%S")  
**Tool:** collect-metrics.sh  
**Version:** 1.0

---

## Executive Summary

EOF

# Function to count lines of code
count_loc() {
    echo -e "${BLUE}Counting lines of code...${NC}"
    
    echo "### Lines of Code" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if command -v cloc &> /dev/null; then
        echo '```' >> "$OUTPUT_FILE"
        cloc . --exclude-dir=node_modules,venv,__pycache__,.git,dist,build,.pytest_cache --quiet >> "$OUTPUT_FILE" 2>/dev/null || echo "cloc failed" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
    else
        echo "**Manual Count (approximate):**" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        # Fallback: manual counting
        for ext in py js ts jsx tsx java go rs c cpp; do
            COUNT=$(find . -name "*.$ext" -not -path '*/node_modules/*' -not -path '*/venv/*' -not -path '*/__pycache__/*' -not -path '*/.git/*' -not -path '*/dist/*' -not -path '*/build/*' -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
            if [ "$COUNT" != "0" ]; then
                echo "- .$ext files: $COUNT lines" >> "$OUTPUT_FILE"
            fi
        done
        
        echo "" >> "$OUTPUT_FILE"
        echo "*Install cloc for detailed metrics: \`brew install cloc\` or \`apt-get install cloc\`*" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze Python code
analyze_python_metrics() {
    if [ ! -d "." ] || [ $(find . -name "*.py" -not -path '*/venv/*' -not -path '*/__pycache__/*' | wc -l) -eq 0 ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing Python code quality...${NC}"
    
    echo "### Python Code Quality" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Radon - Cyclomatic Complexity
    if command -v radon &> /dev/null; then
        echo "#### Cyclomatic Complexity (Radon)" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        radon cc . -a -s --exclude "venv/*,__pycache__/*,build/*,dist/*" 2>/dev/null | head -30 >> "$OUTPUT_FILE" || echo "radon cc failed" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        echo "#### Maintainability Index (Radon)" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        radon mi . -s --exclude "venv/*,__pycache__/*,build/*,dist/*" 2>/dev/null | head -30 >> "$OUTPUT_FILE" || echo "radon mi failed" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    else
        echo "*radon not installed - cannot calculate complexity metrics*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "Install with: \`pip install radon\`" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    # Pylint
    if command -v pylint &> /dev/null; then
        echo "#### Pylint Score" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        pylint --recursive=y . --ignore=venv,__pycache__,build,dist 2>/dev/null | tail -10 >> "$OUTPUT_FILE" || echo "pylint failed or no Python files" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze JavaScript/TypeScript code
analyze_javascript_metrics() {
    if [ ! -f "package.json" ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing JavaScript/TypeScript code quality...${NC}"
    
    echo "### JavaScript/TypeScript Code Quality" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # ESLint
    if command -v eslint &> /dev/null || [ -f "node_modules/.bin/eslint" ]; then
        echo "#### ESLint Results" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        
        if [ -f "node_modules/.bin/eslint" ]; then
            ./node_modules/.bin/eslint . --ext .js,.jsx,.ts,.tsx --max-warnings 0 2>/dev/null | head -50 >> "$OUTPUT_FILE" || echo "ESLint found issues or not configured" >> "$OUTPUT_FILE"
        else
            eslint . --ext .js,.jsx,.ts,.tsx --max-warnings 0 2>/dev/null | head -50 >> "$OUTPUT_FILE" || echo "ESLint found issues or not configured" >> "$OUTPUT_FILE"
        fi
        
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    else
        echo "*ESLint not installed*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to check code duplication
check_duplication() {
    echo -e "${BLUE}Checking for code duplication...${NC}"
    
    echo "### Code Duplication" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if command -v jscpd &> /dev/null; then
        echo '```' >> "$OUTPUT_FILE"
        jscpd . --ignore "node_modules/**,venv/**,__pycache__/**,.git/**,dist/**,build/**" --min-lines 5 --min-tokens 50 2>/dev/null | head -50 >> "$OUTPUT_FILE" || echo "jscpd failed or no duplication found" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
    else
        echo "*jscpd not installed - cannot check for duplication*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "Install with: \`npm install -g jscpd\`" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze test coverage
analyze_test_coverage() {
    echo -e "${BLUE}Analyzing test coverage...${NC}"
    
    echo "### Test Coverage" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Python coverage
    if [ -f ".coverage" ] || [ -f "coverage.xml" ]; then
        echo "#### Python Coverage" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        if command -v coverage &> /dev/null; then
            echo '```' >> "$OUTPUT_FILE"
            coverage report 2>/dev/null | head -30 >> "$OUTPUT_FILE" || echo "coverage report failed" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
        else
            echo "*coverage tool not installed*" >> "$OUTPUT_FILE"
        fi
        echo "" >> "$OUTPUT_FILE"
    fi
    
    # JavaScript coverage
    if [ -d "coverage" ]; then
        echo "#### JavaScript Coverage" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        if [ -f "coverage/coverage-summary.json" ]; then
            echo '```json' >> "$OUTPUT_FILE"
            cat coverage/coverage-summary.json 2>/dev/null | head -20 >> "$OUTPUT_FILE" || echo "coverage summary not found" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
        else
            echo "*Coverage summary available in coverage/ directory*" >> "$OUTPUT_FILE"
        fi
        echo "" >> "$OUTPUT_FILE"
    fi
    
    if [ ! -f ".coverage" ] && [ ! -f "coverage.xml" ] && [ ! -d "coverage" ]; then
        echo "*No coverage data found. Run tests with coverage enabled.*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "Python: \`pytest --cov=src tests/\`" >> "$OUTPUT_FILE"
        echo "JavaScript: \`npm test -- --coverage\`" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to count test files
count_tests() {
    echo -e "${BLUE}Counting test files...${NC}"
    
    echo "### Test Statistics" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Python tests
    PY_TESTS=$(find . -name "test_*.py" -o -name "*_test.py" -not -path '*/venv/*' -not -path '*/__pycache__/*' 2>/dev/null | wc -l | tr -d ' ')
    
    # JavaScript tests
    JS_TESTS=$(find . -name "*.test.js" -o -name "*.spec.js" -o -name "*.test.ts" -o -name "*.spec.ts" -not -path '*/node_modules/*' 2>/dev/null | wc -l | tr -d ' ')
    
    # Go tests
    GO_TESTS=$(find . -name "*_test.go" 2>/dev/null | wc -l | tr -d ' ')
    
    echo "| Language | Test Files |" >> "$OUTPUT_FILE"
    echo "|----------|------------|" >> "$OUTPUT_FILE"
    [ "$PY_TESTS" -gt 0 ] && echo "| Python | $PY_TESTS |" >> "$OUTPUT_FILE"
    [ "$JS_TESTS" -gt 0 ] && echo "| JavaScript/TypeScript | $JS_TESTS |" >> "$OUTPUT_FILE"
    [ "$GO_TESTS" -gt 0 ] && echo "| Go | $GO_TESTS |" >> "$OUTPUT_FILE"
    
    TOTAL_TESTS=$((PY_TESTS + JS_TESTS + GO_TESTS))
    echo "| **Total** | **$TOTAL_TESTS** |" >> "$OUTPUT_FILE"
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to generate summary
generate_summary() {
    echo "## Summary & Recommendations" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Key Metrics" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "- Lines of code analyzed" >> "$OUTPUT_FILE"
    echo "- Code quality scores calculated" >> "$OUTPUT_FILE"
    echo "- Duplication checked" >> "$OUTPUT_FILE"
    echo "- Test coverage analyzed" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Recommendations" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "1. **Complexity:** Keep cyclomatic complexity below 10" >> "$OUTPUT_FILE"
    echo "2. **Maintainability:** Aim for maintainability index above 65" >> "$OUTPUT_FILE"
    echo "3. **Duplication:** Refactor duplicated code (DRY principle)" >> "$OUTPUT_FILE"
    echo "4. **Coverage:** Target 80%+ test coverage" >> "$OUTPUT_FILE"
    echo "5. **Quality:** Address linter warnings and errors" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Tools Used" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    command -v cloc &> /dev/null && echo "- ✅ cloc (line counting)" >> "$OUTPUT_FILE" || echo "- ❌ cloc (not installed)" >> "$OUTPUT_FILE"
    command -v radon &> /dev/null && echo "- ✅ radon (Python complexity)" >> "$OUTPUT_FILE" || echo "- ❌ radon (not installed)" >> "$OUTPUT_FILE"
    command -v pylint &> /dev/null && echo "- ✅ pylint (Python linting)" >> "$OUTPUT_FILE" || echo "- ❌ pylint (not installed)" >> "$OUTPUT_FILE"
    command -v eslint &> /dev/null && echo "- ✅ eslint (JavaScript linting)" >> "$OUTPUT_FILE" || echo "- ❌ eslint (not installed)" >> "$OUTPUT_FILE"
    command -v jscpd &> /dev/null && echo "- ✅ jscpd (duplication detection)" >> "$OUTPUT_FILE" || echo "- ❌ jscpd (not installed)" >> "$OUTPUT_FILE"
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "*Generated by collect-metrics.sh - Part of Bob Shell Knowledge Manager*" >> "$OUTPUT_FILE"
}

# Run all metric collectors
count_loc
analyze_python_metrics
analyze_javascript_metrics
check_duplication
analyze_test_coverage
count_tests
generate_summary

echo -e "${GREEN}✅ Code metrics collection complete!${NC}"
echo -e "${YELLOW}📄 Report saved to: $OUTPUT_FILE${NC}"
echo ""
echo "Next steps:"
echo "1. Review metrics report"
echo "2. Address high complexity areas"
echo "3. Run security-scan.sh for security analysis"
