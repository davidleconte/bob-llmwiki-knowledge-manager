#!/bin/bash
set -e

# analyze-git-history.sh
# Analyzes git history for insights on code churn, contributors, and hotspots
# Usage: ./scripts/analyze-git-history.sh [output-file]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default output location
OUTPUT_FILE="${1:-docs/knowledge-base/research/git-analysis-$(date +%Y-%m-%d).md}"

echo -e "${GREEN}📊 Analyzing Git History...${NC}"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Not a git repository${NC}"
    exit 1
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Start generating report
cat > "$OUTPUT_FILE" << EOF
# Git History Analysis Report

**Generated:** $(date +"%Y-%m-%d %H:%M:%S")  
**Tool:** analyze-git-history.sh  
**Version:** 1.0

---

## Executive Summary

EOF

# Function to analyze commit frequency
analyze_commit_frequency() {
    echo -e "${BLUE}Analyzing commit frequency...${NC}"
    
    echo "### Commit Frequency" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Total commits
    TOTAL_COMMITS=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    echo "**Total Commits:** $TOTAL_COMMITS" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Commits by month (last 12 months)
    echo "#### Commits by Month (Last 12 Months)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| Month | Commits |" >> "$OUTPUT_FILE"
    echo "|-------|---------|" >> "$OUTPUT_FILE"
    
    for i in {0..11}; do
        MONTH=$(date -v-${i}m +"%Y-%m" 2>/dev/null || date -d "${i} months ago" +"%Y-%m" 2>/dev/null)
        if [ -n "$MONTH" ]; then
            COUNT=$(git log --since="$MONTH-01" --until="$MONTH-31" --oneline 2>/dev/null | wc -l | tr -d ' ')
            echo "| $MONTH | $COUNT |" >> "$OUTPUT_FILE"
        fi
    done
    
    echo "" >> "$OUTPUT_FILE"
    
    # Commits by day of week
    echo "#### Commits by Day of Week" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| Day | Commits |" >> "$OUTPUT_FILE"
    echo "|-----|---------|" >> "$OUTPUT_FILE"
    
    for day in Monday Tuesday Wednesday Thursday Friday Saturday Sunday; do
        COUNT=$(git log --format="%ad" --date=format:"%A" 2>/dev/null | grep -c "^$day$" || echo "0")
        echo "| $day | $COUNT |" >> "$OUTPUT_FILE"
    done
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze contributors
analyze_contributors() {
    echo -e "${BLUE}Analyzing contributors...${NC}"
    
    echo "### Contributors" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Total contributors
    TOTAL_CONTRIBUTORS=$(git log --format='%aN' | sort -u | wc -l | tr -d ' ')
    echo "**Total Contributors:** $TOTAL_CONTRIBUTORS" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Top contributors by commit count
    echo "#### Top Contributors (by commits)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| Contributor | Commits | Percentage |" >> "$OUTPUT_FILE"
    echo "|-------------|---------|------------|" >> "$OUTPUT_FILE"
    
    git log --format='%aN' | sort | uniq -c | sort -rn | head -10 | while read count name; do
        PERCENT=$(awk "BEGIN {printf \"%.1f\", ($count/$TOTAL_COMMITS)*100}")
        echo "| $name | $count | $PERCENT% |" >> "$OUTPUT_FILE"
    done
    
    echo "" >> "$OUTPUT_FILE"
    
    # Lines changed by contributor
    echo "#### Top Contributors (by lines changed)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| Contributor | Lines Added | Lines Deleted | Net Change |" >> "$OUTPUT_FILE"
    echo "|-------------|-------------|---------------|------------|" >> "$OUTPUT_FILE"
    
    git log --format='%aN' --numstat | awk '
        NF==3 {
            added[$3]+=$1
            deleted[$3]+=$2
        }
        END {
            for (name in added) {
                printf "| %s | %d | %d | %d |\n", name, added[name], deleted[name], added[name]-deleted[name]
            }
        }
    ' | sort -t'|' -k4 -rn | head -10 >> "$OUTPUT_FILE"
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to identify code churn hotspots
analyze_code_churn() {
    echo -e "${BLUE}Analyzing code churn...${NC}"
    
    echo "### Code Churn Hotspots" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "*Files that change frequently may indicate instability or high complexity*" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Most frequently changed files
    echo "#### Most Frequently Changed Files" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| File | Changes | Risk Level |" >> "$OUTPUT_FILE"
    echo "|------|---------|------------|" >> "$OUTPUT_FILE"
    
    git log --name-only --format="" | grep -v '^$' | sort | uniq -c | sort -rn | head -20 | while read count file; do
        if [ $count -gt 50 ]; then
            RISK="🔴 High"
        elif [ $count -gt 20 ]; then
            RISK="🟡 Medium"
        else
            RISK="🟢 Low"
        fi
        echo "| $file | $count | $RISK |" >> "$OUTPUT_FILE"
    done
    
    echo "" >> "$OUTPUT_FILE"
    
    # Files with most lines changed
    echo "#### Files with Most Lines Changed" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| File | Lines Changed |" >> "$OUTPUT_FILE"
    echo "|------|---------------|" >> "$OUTPUT_FILE"
    
    git log --numstat --format="" | awk '{
        if (NF==3) {
            changes[$3] += $1 + $2
        }
    }
    END {
        for (file in changes) {
            printf "%d %s\n", changes[file], file
        }
    }' | sort -rn | head -20 | while read lines file; do
        echo "| $file | $lines |" >> "$OUTPUT_FILE"
    done
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze recent activity
analyze_recent_activity() {
    echo -e "${BLUE}Analyzing recent activity...${NC}"
    
    echo "### Recent Activity (Last 30 Days)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Commits in last 30 days
    RECENT_COMMITS=$(git log --since="30 days ago" --oneline 2>/dev/null | wc -l | tr -d ' ')
    echo "**Commits:** $RECENT_COMMITS" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Active contributors in last 30 days
    echo "#### Active Contributors" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| Contributor | Commits |" >> "$OUTPUT_FILE"
    echo "|-------------|---------|" >> "$OUTPUT_FILE"
    
    git log --since="30 days ago" --format='%aN' | sort | uniq -c | sort -rn | head -10 | while read count name; do
        echo "| $name | $count |" >> "$OUTPUT_FILE"
    done
    
    echo "" >> "$OUTPUT_FILE"
    
    # Most changed files recently
    echo "#### Recently Modified Files" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| File | Changes |" >> "$OUTPUT_FILE"
    echo "|------|---------|" >> "$OUTPUT_FILE"
    
    git log --since="30 days ago" --name-only --format="" | grep -v '^$' | sort | uniq -c | sort -rn | head -15 | while read count file; do
        echo "| $file | $count |" >> "$OUTPUT_FILE"
    done
    
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze release history
analyze_releases() {
    echo -e "${BLUE}Analyzing release history...${NC}"
    
    echo "### Release History" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Check for tags
    TAG_COUNT=$(git tag | wc -l | tr -d ' ')
    
    if [ "$TAG_COUNT" -gt 0 ]; then
        echo "**Total Releases/Tags:** $TAG_COUNT" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        
        echo "#### Recent Releases" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "| Tag | Date | Commits Since |" >> "$OUTPUT_FILE"
        echo "|-----|------|---------------|" >> "$OUTPUT_FILE"
        
        git tag --sort=-creatordate | head -10 | while read tag; do
            DATE=$(git log -1 --format=%ai "$tag" 2>/dev/null | cut -d' ' -f1)
            COMMITS=$(git rev-list "$tag"..HEAD --count 2>/dev/null || echo "0")
            echo "| $tag | $DATE | $COMMITS |" >> "$OUTPUT_FILE"
        done
        
        echo "" >> "$OUTPUT_FILE"
    else
        echo "*No tags/releases found*" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to analyze commit messages
analyze_commit_messages() {
    echo -e "${BLUE}Analyzing commit messages...${NC}"
    
    echo "### Commit Message Analysis" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Common commit prefixes
    echo "#### Common Commit Types" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "| Type | Count |" >> "$OUTPUT_FILE"
    echo "|------|-------|" >> "$OUTPUT_FILE"
    
    for prefix in "feat:" "fix:" "docs:" "style:" "refactor:" "test:" "chore:" "perf:"; do
        COUNT=$(git log --oneline | grep -c "^[a-f0-9]* $prefix" || echo "0")
        if [ "$COUNT" -gt 0 ]; then
            echo "| $prefix | $COUNT |" >> "$OUTPUT_FILE"
        fi
    done
    
    echo "" >> "$OUTPUT_FILE"
    
    # Average commit message length
    AVG_LENGTH=$(git log --format='%s' | awk '{sum+=length; count++} END {if(count>0) printf "%.0f", sum/count; else print "0"}')
    echo "**Average Commit Message Length:** $AVG_LENGTH characters" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to generate summary
generate_summary() {
    echo "## Summary & Insights" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Key Findings" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "1. **Activity Level:** $TOTAL_COMMITS total commits" >> "$OUTPUT_FILE"
    echo "2. **Team Size:** $TOTAL_CONTRIBUTORS contributors" >> "$OUTPUT_FILE"
    echo "3. **Recent Activity:** $RECENT_COMMITS commits in last 30 days" >> "$OUTPUT_FILE"
    echo "4. **Releases:** $TAG_COUNT tagged releases" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "### Recommendations" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "1. **Hotspots:** Review frequently changed files for refactoring opportunities" >> "$OUTPUT_FILE"
    echo "2. **Code Ownership:** Ensure critical files have multiple maintainers" >> "$OUTPUT_FILE"
    echo "3. **Commit Quality:** Encourage descriptive commit messages" >> "$OUTPUT_FILE"
    echo "4. **Release Cadence:** Consider regular release schedule if not already in place" >> "$OUTPUT_FILE"
    echo "5. **Documentation:** Update docs for frequently changed areas" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "*Generated by analyze-git-history.sh - Part of Bob Shell Knowledge Manager*" >> "$OUTPUT_FILE"
}

# Run all analyzers
analyze_commit_frequency
analyze_contributors
analyze_code_churn
analyze_recent_activity
analyze_releases
analyze_commit_messages
generate_summary

echo -e "${GREEN}✅ Git history analysis complete!${NC}"
echo -e "${YELLOW}📄 Report saved to: $OUTPUT_FILE${NC}"
echo ""
echo "Next steps:"
echo "1. Review git history insights"
echo "2. Identify high-risk areas (frequent changes)"
echo "3. Run check-documentation.sh for documentation coverage"
