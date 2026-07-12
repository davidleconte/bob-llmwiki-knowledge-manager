#!/bin/bash
set -e

# generate-analysis-report.sh
# Consolidates all analysis reports into a comprehensive repository analysis
# Usage: ./scripts/generate-analysis-report.sh [output-file]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Default output location
OUTPUT_FILE="${1:-docs/knowledge-base/guides/complete-repository-analysis.md}"

echo -e "${GREEN}📊 Generating Comprehensive Repository Analysis...${NC}"
echo ""

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Get repository name
REPO_NAME=$(basename "$(pwd)")

# Start generating consolidated report
cat > "$OUTPUT_FILE" << EOF
# Complete Repository Analysis: $REPO_NAME

**Generated:** $(date +"%Y-%m-%d %H:%M:%S")  
**Tool:** generate-analysis-report.sh  
**Version:** 1.0

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Repository Overview](#repository-overview)
3. [Dependency Analysis](#dependency-analysis)
4. [Code Quality Metrics](#code-quality-metrics)
5. [Security Assessment](#security-assessment)
6. [Test Coverage](#test-coverage)
7. [Git History Insights](#git-history-insights)
8. [Documentation Coverage](#documentation-coverage)
9. [Recommendations](#recommendations)
10. [Action Items](#action-items)

---

## Executive Summary

This comprehensive analysis provides insights into the current state of the **$REPO_NAME** repository across multiple dimensions: structure, dependencies, code quality, security, testing, version control history, and documentation.

EOF

# Function to check if a report exists and include it
include_report() {
    local report_pattern="$1"
    local section_title="$2"
    local report_file=""
    
    # Find the most recent report matching the pattern
    report_file=$(find docs/knowledge-base -name "$report_pattern" -type f 2>/dev/null | sort -r | head -1)
    
    if [ -n "$report_file" ] && [ -f "$report_file" ]; then
        echo -e "${BLUE}Including: $section_title${NC}"
        echo "" >> "$OUTPUT_FILE"
        echo "---" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "## $section_title" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "*Source: \`$report_file\`*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        # Extract key sections (skip the header and metadata)
        sed -n '/^## /,/^---$/p' "$report_file" | head -100 >> "$OUTPUT_FILE"
        
        echo "" >> "$OUTPUT_FILE"
        echo "*For full details, see: [\`$report_file\`]($report_file)*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        return 0
    else
        echo -e "${YELLOW}⚠️  Report not found: $report_pattern${NC}"
        echo "" >> "$OUTPUT_FILE"
        echo "---" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "## $section_title" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "⚠️  **Report not available.** Run the corresponding analysis script:" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        case "$report_pattern" in
            "repo-scan-*.md")
                echo "- \`./scripts/scan-repository.sh\`" >> "$OUTPUT_FILE"
                ;;
            "dependency-analysis.md")
                echo "- \`./scripts/analyze-dependencies.sh\`" >> "$OUTPUT_FILE"
                ;;
            "code-metrics-*.md")
                echo "- \`./scripts/collect-metrics.sh\`" >> "$OUTPUT_FILE"
                ;;
            "security-scan-*.md")
                echo "- \`./scripts/security-scan.sh\`" >> "$OUTPUT_FILE"
                ;;
            "test-coverage-*.md")
                echo "- \`./scripts/test-coverage.sh\`" >> "$OUTPUT_FILE"
                ;;
            "git-analysis-*.md")
                echo "- \`./scripts/analyze-git-history.sh\`" >> "$OUTPUT_FILE"
                ;;
            "doc-coverage-*.md")
                echo "- \`./scripts/check-documentation.sh\`" >> "$OUTPUT_FILE"
                ;;
        esac
        
        echo "" >> "$OUTPUT_FILE"
        return 1
    fi
}

# Include all reports
include_report "repo-scan-*.md" "Repository Overview"
include_report "dependency-analysis.md" "Dependency Analysis"
include_report "code-metrics-*.md" "Code Quality Metrics"
include_report "security-scan-*.md" "Security Assessment"
include_report "test-coverage-*.md" "Test Coverage"
include_report "git-analysis-*.md" "Git History Insights"
include_report "doc-coverage-*.md" "Documentation Coverage"

# Generate consolidated recommendations
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Recommendations" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Based on the comprehensive analysis, here are prioritized recommendations:" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 🔴 Critical (Immediate Action Required)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "1. **Security Vulnerabilities:** Address any critical or high-severity security issues" >> "$OUTPUT_FILE"
echo "2. **Missing Tests:** Add tests for critical code paths with no coverage" >> "$OUTPUT_FILE"
echo "3. **Exposed Secrets:** Remove any hardcoded credentials or API keys" >> "$OUTPUT_FILE"
echo "4. **Breaking Changes:** Fix any breaking API changes or deprecated dependencies" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 🟡 High Priority (Within 1-2 Weeks)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "1. **Code Quality:** Refactor high-complexity functions (cyclomatic complexity >10)" >> "$OUTPUT_FILE"
echo "2. **Documentation:** Add missing docstrings and API documentation" >> "$OUTPUT_FILE"
echo "3. **Test Coverage:** Increase coverage to 80%+ for core modules" >> "$OUTPUT_FILE"
echo "4. **Dependency Updates:** Update outdated dependencies with known issues" >> "$OUTPUT_FILE"
echo "5. **Code Duplication:** Refactor duplicated code blocks" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 🟢 Medium Priority (Within 1 Month)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "1. **Code Hotspots:** Review and stabilize frequently changed files" >> "$OUTPUT_FILE"
echo "2. **Performance:** Optimize identified performance bottlenecks" >> "$OUTPUT_FILE"
echo "3. **Linting:** Address linter warnings and style inconsistencies" >> "$OUTPUT_FILE"
echo "4. **README:** Enhance README with better examples and setup instructions" >> "$OUTPUT_FILE"
echo "5. **CI/CD:** Improve automated testing and deployment pipelines" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 🔵 Low Priority (Nice to Have)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "1. **Code Comments:** Improve inline documentation" >> "$OUTPUT_FILE"
echo "2. **Examples:** Add more usage examples and tutorials" >> "$OUTPUT_FILE"
echo "3. **Tooling:** Set up additional development tools (formatters, pre-commit hooks)" >> "$OUTPUT_FILE"
echo "4. **Monitoring:** Add observability and logging improvements" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Generate action items
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Action Items" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "### Immediate Actions (This Week)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "- [ ] Review and triage all critical security vulnerabilities" >> "$OUTPUT_FILE"
echo "- [ ] Create issues for high-priority items" >> "$OUTPUT_FILE"
echo "- [ ] Update dependencies with security patches" >> "$OUTPUT_FILE"
echo "- [ ] Document any breaking changes or migration paths" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### Short-term Actions (Next 2-4 Weeks)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "- [ ] Implement missing tests for critical paths" >> "$OUTPUT_FILE"
echo "- [ ] Refactor high-complexity code" >> "$OUTPUT_FILE"
echo "- [ ] Update documentation (README, API docs, docstrings)" >> "$OUTPUT_FILE"
echo "- [ ] Address code duplication" >> "$OUTPUT_FILE"
echo "- [ ] Set up automated security scanning in CI/CD" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### Long-term Actions (Next 1-3 Months)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "- [ ] Achieve 80%+ test coverage" >> "$OUTPUT_FILE"
echo "- [ ] Stabilize code hotspots" >> "$OUTPUT_FILE"
echo "- [ ] Implement comprehensive monitoring" >> "$OUTPUT_FILE"
echo "- [ ] Create developer onboarding guide" >> "$OUTPUT_FILE"
echo "- [ ] Establish code review guidelines" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Add analysis metadata
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Analysis Metadata" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**Repository:** $REPO_NAME" >> "$OUTPUT_FILE"
echo "**Analysis Date:** $(date +"%Y-%m-%d %H:%M:%S")" >> "$OUTPUT_FILE"
echo "**Generated By:** Bob Shell Knowledge Manager" >> "$OUTPUT_FILE"
echo "**Tool Version:** 1.0" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### Reports Included" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# List all included reports
find docs/knowledge-base -name "repo-scan-*.md" -o -name "dependency-analysis.md" -o -name "code-metrics-*.md" -o -name "security-scan-*.md" -o -name "test-coverage-*.md" -o -name "git-analysis-*.md" -o -name "doc-coverage-*.md" 2>/dev/null | sort | while read report; do
    echo "- \`$report\`" >> "$OUTPUT_FILE"
done

echo "" >> "$OUTPUT_FILE"

echo "### How to Update This Report" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "To regenerate this comprehensive analysis:" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
echo "# Run all analysis scripts" >> "$OUTPUT_FILE"
echo "./scripts/scan-repository.sh" >> "$OUTPUT_FILE"
echo "./scripts/analyze-dependencies.sh" >> "$OUTPUT_FILE"
echo "./scripts/collect-metrics.sh" >> "$OUTPUT_FILE"
echo "./scripts/security-scan.sh" >> "$OUTPUT_FILE"
echo "./scripts/test-coverage.sh" >> "$OUTPUT_FILE"
echo "./scripts/analyze-git-history.sh" >> "$OUTPUT_FILE"
echo "./scripts/check-documentation.sh" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "# Generate consolidated report" >> "$OUTPUT_FILE"
echo "./scripts/generate-analysis-report.sh" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "*Generated by generate-analysis-report.sh - Part of Bob Shell Knowledge Manager*" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "*This report consolidates findings from multiple analysis tools to provide a comprehensive view of the repository's health and areas for improvement.*" >> "$OUTPUT_FILE"

echo ""
echo -e "${GREEN}✅ Comprehensive analysis report generated!${NC}"
echo -e "${YELLOW}📄 Report saved to: $OUTPUT_FILE${NC}"
echo ""
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}  Repository Analysis Complete!${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Summary of available reports:"
echo "1. Repository scan"
echo "2. Dependency analysis"
echo "3. Code quality metrics"
echo "4. Security assessment"
echo "5. Test coverage"
echo "6. Git history insights"
echo "7. Documentation coverage"
echo "8. Consolidated analysis (this report)"
echo ""
echo "Next steps:"
echo "1. Review the consolidated report"
echo "2. Prioritize action items"
echo "3. Create issues for high-priority items"
echo "4. Share findings with the team"
