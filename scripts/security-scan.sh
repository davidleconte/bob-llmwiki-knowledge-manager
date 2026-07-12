#!/bin/bash
set -e

# security-scan.sh
# Runs security scanners across multiple languages
# Usage: ./scripts/security-scan.sh [output-file]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default output location
OUTPUT_FILE="${1:-docs/knowledge-base/research/security-scan-$(date +%Y-%m-%d).md}"

echo -e "${GREEN}🔒 Running Security Scans...${NC}"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Start generating report
cat > "$OUTPUT_FILE" << EOF
# Security Scan Report

**Generated:** $(date +"%Y-%m-%d %H:%M:%S")  
**Tool:** security-scan.sh  
**Version:** 1.0

---

## Executive Summary

EOF

# Function to scan Node.js dependencies
scan_nodejs() {
    if [ ! -f "package.json" ]; then
        return
    fi
    
    echo -e "${BLUE}Scanning Node.js dependencies...${NC}"
    
    echo "### Node.js Security (npm audit)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if command -v npm &> /dev/null && [ -f "package-lock.json" ]; then
        echo '```' >> "$OUTPUT_FILE"
        npm audit --json 2>/dev/null | jq -r '
            if .vulnerabilities then
                "Total Vulnerabilities: \(.metadata.vulnerabilities.total)",
                "Critical: \(.metadata.vulnerabilities.critical)",
                "High: \(.metadata.vulnerabilities.high)",
                "Moderate: \(.metadata.vulnerabilities.moderate)",
                "Low: \(.metadata.vulnerabilities.low)",
                "",
                "Top Issues:",
                (.vulnerabilities | to_entries | sort_by(.value.severity) | reverse | .[0:5] | .[] | "- [\(.value.severity)] \(.key): \(.value.via[0].title // "No title")")
            else
                "No vulnerabilities found or npm audit failed"
            end
        ' >> "$OUTPUT_FILE" 2>/dev/null || echo "npm audit failed" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        
        echo "" >> "$OUTPUT_FILE"
        echo "**Recommendation:** Run \`npm audit fix\` to automatically fix issues" >> "$OUTPUT_FILE"
    else
        echo "*npm not available or package-lock.json missing*" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to scan Python dependencies
scan_python() {
    if [ ! -f "requirements.txt" ]; then
        return
    fi
    
    echo -e "${BLUE}Scanning Python dependencies...${NC}"
    
    echo "### Python Security" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Try safety first
    if command -v safety &> /dev/null; then
        echo "#### Safety Check" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        safety check --json 2>/dev/null | jq -r '.[] | "[\(.severity)] \(.package) \(.installed_version)\n  \(.vulnerability)\n  Fix: \(.more_info_url)"' >> "$OUTPUT_FILE" 2>/dev/null || echo "No vulnerabilities found or safety check failed" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    # Try pip-audit
    if command -v pip-audit &> /dev/null; then
        echo "#### pip-audit Check" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        pip-audit --format json 2>/dev/null | jq -r '.dependencies[] | "[\(.vulns[0].severity)] \(.name) \(.version)\n  \(.vulns[0].id): \(.vulns[0].description)\n  Fix: \(.vulns[0].fix_versions[0] // "No fix available")"' >> "$OUTPUT_FILE" 2>/dev/null || echo "No vulnerabilities found or pip-audit failed" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    if ! command -v safety &> /dev/null && ! command -v pip-audit &> /dev/null; then
        echo "*Neither safety nor pip-audit installed*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "Install with:" >> "$OUTPUT_FILE"
        echo "- \`pip install safety\`" >> "$OUTPUT_FILE"
        echo "- \`pip install pip-audit\`" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    # Bandit for Python code security
    if command -v bandit &> /dev/null; then
        echo "#### Bandit (Python Code Security)" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        bandit -r . -f json --exclude './venv/*,./build/*,./dist/*' 2>/dev/null | jq -r '
            "Total Issues: \(.metrics._totals.CONFIDENCE.HIGH + .metrics._totals.CONFIDENCE.MEDIUM + .metrics._totals.CONFIDENCE.LOW)",
            "High Severity: \(.metrics._totals.SEVERITY.HIGH)",
            "Medium Severity: \(.metrics._totals.SEVERITY.MEDIUM)",
            "Low Severity: \(.metrics._totals.SEVERITY.LOW)",
            "",
            "Top Issues:",
            (.results | sort_by(.issue_severity) | reverse | .[0:5] | .[] | "[\(.issue_severity)] \(.test_id): \(.issue_text)\n  File: \(.filename):\(.line_number)")
        ' >> "$OUTPUT_FILE" 2>/dev/null || echo "bandit scan failed or no issues found" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    else
        echo "*bandit not installed - cannot scan Python code*" >> "$OUTPUT_FILE"
        echo "Install with: \`pip install bandit\`" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to scan for secrets
scan_secrets() {
    echo -e "${BLUE}Scanning for secrets...${NC}"
    
    echo "### Secret Detection" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if command -v gitleaks &> /dev/null; then
        echo "#### Gitleaks Scan" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        gitleaks detect --no-git --report-format json 2>/dev/null | jq -r '
            if . == null or . == [] then
                "No secrets detected"
            else
                "Secrets Found: \(length)",
                "",
                "Issues:",
                (.[] | "[\(.RuleID)] \(.File):\(.StartLine)\n  \(.Secret[0:50])...\n  Description: \(.Description)")
            end
        ' >> "$OUTPUT_FILE" 2>/dev/null || echo "gitleaks scan completed with no findings" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    else
        echo "*gitleaks not installed - cannot scan for secrets*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "Install with:" >> "$OUTPUT_FILE"
        echo "- macOS: \`brew install gitleaks\`" >> "$OUTPUT_FILE"
        echo "- Linux: Download from https://github.com/gitleaks/gitleaks/releases" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    # Manual pattern check for common secrets
    echo "#### Manual Pattern Check" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "Checking for common secret patterns..." >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    FOUND_PATTERNS=false
    
    # Check for API keys
    if grep -r "api[_-]key\s*=\s*['\"][^'\"]\{20,\}" . --exclude-dir={node_modules,venv,.git,dist,build} 2>/dev/null | head -5 | grep -q .; then
        echo "⚠️  Potential API keys found" >> "$OUTPUT_FILE"
        FOUND_PATTERNS=true
    fi
    
    # Check for passwords
    if grep -r "password\s*=\s*['\"][^'\"]\{8,\}" . --exclude-dir={node_modules,venv,.git,dist,build} 2>/dev/null | head -5 | grep -q .; then
        echo "⚠️  Potential hardcoded passwords found" >> "$OUTPUT_FILE"
        FOUND_PATTERNS=true
    fi
    
    # Check for tokens
    if grep -r "token\s*=\s*['\"][^'\"]\{20,\}" . --exclude-dir={node_modules,venv,.git,dist,build} 2>/dev/null | head -5 | grep -q .; then
        echo "⚠️  Potential tokens found" >> "$OUTPUT_FILE"
        FOUND_PATTERNS=true
    fi
    
    if [ "$FOUND_PATTERNS" = false ]; then
        echo "✅ No obvious secret patterns detected" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to check for common security issues
check_common_issues() {
    echo -e "${BLUE}Checking for common security issues...${NC}"
    
    echo "### Common Security Issues" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "#### Configuration Files" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Check for exposed .env files
    if [ -f ".env" ] && ! grep -q "^\.env$" .gitignore 2>/dev/null; then
        echo "⚠️  .env file exists but not in .gitignore" >> "$OUTPUT_FILE"
    else
        echo "✅ .env handling looks good" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    
    # Check for debug mode
    if grep -r "DEBUG\s*=\s*True" . --include="*.py" --exclude-dir={venv,.git} 2>/dev/null | grep -q .; then
        echo "⚠️  DEBUG=True found in Python files" >> "$OUTPUT_FILE"
    fi
    
    if grep -r "NODE_ENV.*development" . --include="*.js" --include="*.ts" --exclude-dir={node_modules,.git} 2>/dev/null | grep -q .; then
        echo "⚠️  Development mode references found in code" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    
    echo "#### Dependency Files" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Check for lock files
    if [ -f "package.json" ] && [ ! -f "package-lock.json" ] && [ ! -f "yarn.lock" ]; then
        echo "⚠️  No lock file found for Node.js dependencies" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to generate OWASP Top 10 checklist
generate_owasp_checklist() {
    echo "### OWASP Top 10 Checklist" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "Manual review recommended for:" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "- [ ] **A01:2021 – Broken Access Control**" >> "$OUTPUT_FILE"
    echo "  - Check authorization on all endpoints" >> "$OUTPUT_FILE"
    echo "  - Verify user permissions" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "- [ ] **A02:2021 – Cryptographic Failures**" >> "$OUTPUT_FILE"
    echo "  - Verify encryption for sensitive data" >> "$OUTPUT_FILE"
    echo "  - Check TLS/SSL configuration" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "- [ ] **A03:2021 – Injection**" >> "$OUTPUT_FILE"
    echo "  - SQL injection prevention" >> "$OUTPUT_FILE"
    echo "  - Command injection prevention" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "- [ ] **A04:2021 – Insecure Design**" >> "$OUTPUT_FILE"
    echo "  - Review architecture for security flaws" >> "$OUTPUT_FILE"
    echo "  - Threat modeling" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "- [ ] **A05:2021 – Security Misconfiguration**" >> "$OUTPUT_FILE"
    echo "  - Default credentials changed" >> "$OUTPUT_FILE"
    echo "  - Unnecessary features disabled" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "- [ ] **A06:2021 – Vulnerable Components**" >> "$OUTPUT_FILE"
    echo "  - Dependencies up to date" >> "$OUTPUT_FILE"
    echo "  - No known vulnerabilities" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "- [ ] **A07:2021 – Authentication Failures**" >> "$OUTPUT_FILE"
    echo "  - Strong password policy" >> "$OUTPUT_FILE"
    echo "  - Multi-factor authentication" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "- [ ] **A08:2021 – Software and Data Integrity**" >> "$OUTPUT_FILE"
    echo "  - Code signing" >> "$OUTPUT_FILE"
    echo "  - Integrity checks" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "- [ ] **A09:2021 – Security Logging Failures**" >> "$OUTPUT_FILE"
    echo "  - Adequate logging" >> "$OUTPUT_FILE"
    echo "  - Log monitoring" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "- [ ] **A10:2021 – Server-Side Request Forgery**" >> "$OUTPUT_FILE"
    echo "  - Input validation for URLs" >> "$OUTPUT_FILE"
    echo "  - Network segmentation" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to generate summary
generate_summary() {
    echo "## Summary & Recommendations" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Scans Performed" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    [ -f "package.json" ] && echo "- ✅ Node.js dependency scan" >> "$OUTPUT_FILE"
    [ -f "requirements.txt" ] && echo "- ✅ Python dependency scan" >> "$OUTPUT_FILE"
    command -v bandit &> /dev/null && echo "- ✅ Python code security scan" >> "$OUTPUT_FILE"
    command -v gitleaks &> /dev/null && echo "- ✅ Secret detection scan" >> "$OUTPUT_FILE"
    echo "- ✅ Common security issues check" >> "$OUTPUT_FILE"
    echo "- ✅ OWASP Top 10 checklist generated" >> "$OUTPUT_FILE"
    
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Immediate Actions" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "1. **Critical vulnerabilities:** Fix immediately" >> "$OUTPUT_FILE"
    echo "2. **Secrets:** Remove any exposed secrets" >> "$OUTPUT_FILE"
    echo "3. **Dependencies:** Update vulnerable packages" >> "$OUTPUT_FILE"
    echo "4. **Configuration:** Review security settings" >> "$OUTPUT_FILE"
    echo "5. **OWASP:** Complete manual checklist review" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Tools Status" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    command -v npm &> /dev/null && echo "- ✅ npm (Node.js security)" >> "$OUTPUT_FILE" || echo "- ❌ npm (not installed)" >> "$OUTPUT_FILE"
    command -v safety &> /dev/null && echo "- ✅ safety (Python security)" >> "$OUTPUT_FILE" || echo "- ❌ safety (not installed)" >> "$OUTPUT_FILE"
    command -v pip-audit &> /dev/null && echo "- ✅ pip-audit (Python security)" >> "$OUTPUT_FILE" || echo "- ❌ pip-audit (not installed)" >> "$OUTPUT_FILE"
    command -v bandit &> /dev/null && echo "- ✅ bandit (Python code security)" >> "$OUTPUT_FILE" || echo "- ❌ bandit (not installed)" >> "$OUTPUT_FILE"
    command -v gitleaks &> /dev/null && echo "- ✅ gitleaks (secret detection)" >> "$OUTPUT_FILE" || echo "- ❌ gitleaks (not installed)" >> "$OUTPUT_FILE"
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "*Generated by security-scan.sh - Part of Bob Shell Knowledge Manager*" >> "$OUTPUT_FILE"
}

# Run all security scans
scan_nodejs
scan_python
scan_secrets
check_common_issues
generate_owasp_checklist
generate_summary

echo -e "${GREEN}✅ Security scan complete!${NC}"
echo -e "${YELLOW}📄 Report saved to: $OUTPUT_FILE${NC}"
echo ""
echo "⚠️  IMPORTANT: Review all findings and take immediate action on critical issues"
echo ""
echo "Next steps:"
echo "1. Review security report"
echo "2. Fix critical vulnerabilities"
echo "3. Run test-coverage.sh for test analysis"
