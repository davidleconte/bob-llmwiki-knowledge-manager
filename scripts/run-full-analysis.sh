#!/bin/bash
set -e

# run-full-analysis.sh
# Master script that runs all repository analysis scripts in sequence
# Usage: ./scripts/run-full-analysis.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}║        Bob Shell Knowledge Manager                         ║${NC}"
echo -e "${CYAN}║        Complete Repository Analysis Suite                  ║${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Starting comprehensive repository analysis...${NC}"
echo ""

# Track start time
START_TIME=$(date +%s)

# Track success/failure
TOTAL_SCRIPTS=7
SUCCESSFUL=0
FAILED=0

# Function to run a script and track results
run_script() {
    local script_name="$1"
    local script_path="$SCRIPT_DIR/$script_name"
    local description="$2"
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Running: $description${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    if [ -f "$script_path" ]; then
        if bash "$script_path"; then
            echo ""
            echo -e "${GREEN}✅ $description completed successfully${NC}"
            SUCCESSFUL=$((SUCCESSFUL + 1))
        else
            echo ""
            echo -e "${RED}❌ $description failed${NC}"
            FAILED=$((FAILED + 1))
        fi
    else
        echo -e "${RED}❌ Script not found: $script_path${NC}"
        FAILED=$((FAILED + 1))
    fi
    
    echo ""
}

# Run all analysis scripts in sequence
echo -e "${MAGENTA}Phase 1: Repository Structure Analysis${NC}"
run_script "scan-repository.sh" "Repository Scan"

echo -e "${MAGENTA}Phase 2: Dependency Analysis${NC}"
run_script "analyze-dependencies.sh" "Dependency Analysis"

echo -e "${MAGENTA}Phase 3: Code Quality Metrics${NC}"
run_script "collect-metrics.sh" "Code Metrics Collection"

echo -e "${MAGENTA}Phase 4: Security Assessment${NC}"
run_script "security-scan.sh" "Security Scan"

echo -e "${MAGENTA}Phase 5: Test Coverage Analysis${NC}"
run_script "test-coverage.sh" "Test Coverage Analysis"

echo -e "${MAGENTA}Phase 6: Git History Analysis${NC}"
run_script "analyze-git-history.sh" "Git History Analysis"

echo -e "${MAGENTA}Phase 7: Documentation Coverage${NC}"
run_script "check-documentation.sh" "Documentation Coverage Check"

# Generate consolidated report
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Generating Consolidated Report${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if bash "$SCRIPT_DIR/generate-analysis-report.sh"; then
    echo ""
    echo -e "${GREEN}✅ Consolidated report generated successfully${NC}"
    SUCCESSFUL=$((SUCCESSFUL + 1))
else
    echo ""
    echo -e "${RED}❌ Consolidated report generation failed${NC}"
    FAILED=$((FAILED + 1))
fi

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

# Print summary
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    Analysis Complete                       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Successful: $SUCCESSFUL / $((TOTAL_SCRIPTS + 1))${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Failed: $FAILED / $((TOTAL_SCRIPTS + 1))${NC}"
fi
echo -e "${YELLOW}⏱️  Duration: ${MINUTES}m ${SECONDS}s${NC}"
echo ""

# List generated reports
echo -e "${CYAN}Generated Reports:${NC}"
echo ""
find docs/knowledge-base -type f \( -name "repo-scan-*.md" -o -name "dependency-analysis.md" -o -name "code-metrics-*.md" -o -name "security-scan-*.md" -o -name "test-coverage-*.md" -o -name "git-analysis-*.md" -o -name "doc-coverage-*.md" -o -name "complete-repository-analysis.md" \) -mtime -1 2>/dev/null | sort | while read report; do
    echo -e "  📄 $report"
done

echo ""
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}  Next Steps:${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "1. Review the consolidated analysis report:"
echo -e "   ${CYAN}docs/knowledge-base/guides/complete-repository-analysis.md${NC}"
echo ""
echo "2. Prioritize action items based on severity"
echo ""
echo "3. Create issues for high-priority items"
echo ""
echo "4. Share findings with your team"
echo ""
echo "5. Schedule regular analysis runs (weekly/monthly)"
echo ""

# Exit with appropriate code
if [ $FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi
