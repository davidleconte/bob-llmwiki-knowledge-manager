#!/bin/bash
set -e

# test-coverage.sh
# Generates test coverage reports for multiple languages
# Usage: ./scripts/test-coverage.sh [output-file]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default output location
OUTPUT_FILE="${1:-docs/knowledge-base/research/test-coverage-$(date +%Y-%m-%d).md}"

echo -e "${GREEN}🧪 Generating Test Coverage Report...${NC}"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Start generating report
cat > "$OUTPUT_FILE" << EOF
# Test Coverage Report

**Generated:** $(date +"%Y-%m-%d %H:%M:%S")  
**Tool:** test-coverage.sh  
**Version:** 1.0

---

## Executive Summary

EOF

# Function to analyze Python test coverage
analyze_python_coverage() {
    if [ ! -f "requirements.txt" ] && [ ! -f "setup.py" ] && [ ! -f "pyproject.toml" ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing Python test coverage...${NC}"
    
    echo "### Python Test Coverage" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Check if pytest is available
    if command -v pytest &> /dev/null; then
        echo "#### Running pytest with coverage..." >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        # Run tests with coverage
        if pytest --cov=. --cov-report=term --cov-report=json tests/ 2>/dev/null; then
            echo '```' >> "$OUTPUT_FILE"
            
            # Parse coverage.json if it exists
            if [ -f "coverage.json" ]; then
                python3 -c "
import json
with open('coverage.json') as f:
    data = json.load(f)
    total = data['totals']
    print(f\"Total Coverage: {total['percent_covered']:.2f}%\")
    print(f\"Lines Covered: {total['covered_lines']}/{total['num_statements']}\")
    print(f\"Missing Lines: {total['missing_lines']}\")
    print(f\"Excluded Lines: {total['excluded_lines']}\")
" >> "$OUTPUT_FILE" 2>/dev/null || echo "Coverage data available in coverage.json" >> "$OUTPUT_FILE"
            else
                pytest --cov=. --cov-report=term tests/ 2>/dev/null | tail -20 >> "$OUTPUT_FILE" || echo "pytest coverage failed" >> "$OUTPUT_FILE"
            fi
            
            echo '```' >> "$OUTPUT_FILE"
        else
            echo "*pytest tests failed or no tests found*" >> "$OUTPUT_FILE"
        fi
        
        echo "" >> "$OUTPUT_FILE"
        
        # Check for HTML coverage report
        if [ -d "htmlcov" ]; then
            echo "**HTML Report:** Available in \`htmlcov/index.html\`" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
        
    elif command -v coverage &> /dev/null; then
        echo "#### Running coverage..." >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        if [ -f ".coverage" ]; then
            echo '```' >> "$OUTPUT_FILE"
            coverage report 2>/dev/null | head -30 >> "$OUTPUT_FILE" || echo "coverage report failed" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
        else
            echo "*No .coverage file found. Run: \`coverage run -m pytest tests/\`*" >> "$OUTPUT_FILE"
        fi
        
        echo "" >> "$OUTPUT_FILE"
    else
        echo "*pytest or coverage not installed*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "Install with: \`pip install pytest pytest-cov\`" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    # Count test files
    TEST_FILES=$(find . -name "test_*.py" -o -name "*_test.py" -not -path '*/venv/*' -not -path '*/__pycache__/*' 2>/dev/null | wc -l | tr -d ' ')
    echo "**Test Files Found:** $TEST_FILES" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze JavaScript/TypeScript coverage
analyze_javascript_coverage() {
    if [ ! -f "package.json" ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing JavaScript/TypeScript test coverage...${NC}"
    
    echo "### JavaScript/TypeScript Test Coverage" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Check if jest or other test runner is configured
    if grep -q "jest" package.json 2>/dev/null; then
        echo "#### Jest Coverage" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        if [ -d "coverage" ]; then
            if [ -f "coverage/coverage-summary.json" ]; then
                echo '```json' >> "$OUTPUT_FILE"
                cat coverage/coverage-summary.json 2>/dev/null | python3 -m json.tool | head -50 >> "$OUTPUT_FILE" || cat coverage/coverage-summary.json >> "$OUTPUT_FILE"
                echo '```' >> "$OUTPUT_FILE"
                echo "" >> "$OUTPUT_FILE"
                
                # Extract summary
                echo "**Summary:**" >> "$OUTPUT_FILE"
                echo '```' >> "$OUTPUT_FILE"
                python3 -c "
import json
with open('coverage/coverage-summary.json') as f:
    data = json.load(f)
    total = data['total']
    print(f\"Lines: {total['lines']['pct']}%\")
    print(f\"Statements: {total['statements']['pct']}%\")
    print(f\"Functions: {total['functions']['pct']}%\")
    print(f\"Branches: {total['branches']['pct']}%\")
" >> "$OUTPUT_FILE" 2>/dev/null || echo "Coverage summary available in coverage/coverage-summary.json" >> "$OUTPUT_FILE"
                echo '```' >> "$OUTPUT_FILE"
                echo "" >> "$OUTPUT_FILE"
            else
                echo "*Coverage directory exists but no summary found*" >> "$OUTPUT_FILE"
                echo "" >> "$OUTPUT_FILE"
            fi
            
            echo "**HTML Report:** Available in \`coverage/lcov-report/index.html\`" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        else
            echo "*No coverage directory found*" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            echo "Run tests with coverage: \`npm test -- --coverage\`" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    else
        echo "*Jest not configured in package.json*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    # Count test files
    TEST_FILES=$(find . -name "*.test.js" -o -name "*.spec.js" -o -name "*.test.ts" -o -name "*.spec.ts" -not -path '*/node_modules/*' 2>/dev/null | wc -l | tr -d ' ')
    echo "**Test Files Found:** $TEST_FILES" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze Go test coverage
analyze_go_coverage() {
    if [ ! -f "go.mod" ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing Go test coverage...${NC}"
    
    echo "### Go Test Coverage" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if command -v go &> /dev/null; then
        echo "#### Running go test with coverage..." >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        echo '```' >> "$OUTPUT_FILE"
        go test -cover ./... 2>/dev/null | head -30 >> "$OUTPUT_FILE" || echo "go test failed or no tests found" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        # Generate detailed coverage
        if go test -coverprofile=coverage.out ./... 2>/dev/null; then
            echo "**Detailed Coverage:**" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
            go tool cover -func=coverage.out 2>/dev/null | tail -20 >> "$OUTPUT_FILE" || echo "coverage details failed" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            
            echo "*HTML report can be generated with: \`go tool cover -html=coverage.out\`*" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    else
        echo "*go not installed*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    # Count test files
    TEST_FILES=$(find . -name "*_test.go" 2>/dev/null | wc -l | tr -d ' ')
    echo "**Test Files Found:** $TEST_FILES" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze Rust test coverage
analyze_rust_coverage() {
    if [ ! -f "Cargo.toml" ]; then
        return
    fi
    
    echo -e "${BLUE}Analyzing Rust test coverage...${NC}"
    
    echo "### Rust Test Coverage" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if command -v cargo &> /dev/null; then
        echo "#### Running cargo test..." >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        echo '```' >> "$OUTPUT_FILE"
        cargo test 2>/dev/null | tail -20 >> "$OUTPUT_FILE" || echo "cargo test failed or no tests found" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        # Check for tarpaulin (coverage tool)
        if command -v cargo-tarpaulin &> /dev/null; then
            echo "**Coverage (tarpaulin):**" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
            cargo tarpaulin --out Stdout 2>/dev/null | tail -20 >> "$OUTPUT_FILE" || echo "tarpaulin failed" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        else
            echo "*cargo-tarpaulin not installed for coverage*" >> "$OUTPUT_FILE"
            echo "Install with: \`cargo install cargo-tarpaulin\`" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    else
        echo "*cargo not installed*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to generate coverage summary
generate_summary() {
    echo "## Coverage Summary" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Languages Analyzed" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    FOUND_TESTS=false
    [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ] && echo "- ✅ Python" >> "$OUTPUT_FILE" && FOUND_TESTS=true
    [ -f "package.json" ] && echo "- ✅ JavaScript/TypeScript" >> "$OUTPUT_FILE" && FOUND_TESTS=true
    [ -f "go.mod" ] && echo "- ✅ Go" >> "$OUTPUT_FILE" && FOUND_TESTS=true
    [ -f "Cargo.toml" ] && echo "- ✅ Rust" >> "$OUTPUT_FILE" && FOUND_TESTS=true
    
    if [ "$FOUND_TESTS" = false ]; then
        echo "- ❌ No test frameworks detected" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Recommendations" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "1. **Target:** Aim for 80%+ code coverage" >> "$OUTPUT_FILE"
    echo "2. **Critical Paths:** Ensure 100% coverage for critical code" >> "$OUTPUT_FILE"
    echo "3. **Test Quality:** Focus on meaningful tests, not just coverage" >> "$OUTPUT_FILE"
    echo "4. **CI/CD:** Integrate coverage checks in CI pipeline" >> "$OUTPUT_FILE"
    echo "5. **Trends:** Track coverage over time" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Coverage Thresholds" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| Level | Coverage | Status |" >> "$OUTPUT_FILE"
    echo "|-------|----------|--------|" >> "$OUTPUT_FILE"
    echo "| Excellent | 90-100% | 🟢 |" >> "$OUTPUT_FILE"
    echo "| Good | 80-89% | 🟡 |" >> "$OUTPUT_FILE"
    echo "| Acceptable | 70-79% | 🟠 |" >> "$OUTPUT_FILE"
    echo "| Poor | <70% | 🔴 |" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "*Generated by test-coverage.sh - Part of Bob Shell Knowledge Manager*" >> "$OUTPUT_FILE"
}

# Run all coverage analyzers
analyze_python_coverage
analyze_javascript_coverage
analyze_go_coverage
analyze_rust_coverage
generate_summary

echo -e "${GREEN}✅ Test coverage analysis complete!${NC}"
echo -e "${YELLOW}📄 Report saved to: $OUTPUT_FILE${NC}"
echo ""
echo "Next steps:"
echo "1. Review coverage report"
echo "2. Identify untested code"
echo "3. Run analyze-git-history.sh for code churn analysis"
