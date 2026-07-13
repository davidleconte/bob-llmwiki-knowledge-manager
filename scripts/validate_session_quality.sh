#!/bin/bash
#
# Session Quality Validator
#
# Validates the quality of collected Bob Shell sessions and provides
# actionable feedback for improvement.
#
# Usage:
#   ./scripts/validate_session_quality.sh [--baseline|--optimized] [--fix]
#
# Options:
#   --baseline    Validate baseline sessions (default)
#   --optimized   Validate optimized sessions
#   --fix         Attempt to fix common issues automatically
#   --verbose     Show detailed validation output
#
# Exit codes:
#   0 - All sessions pass quality checks
#   1 - Some sessions have quality issues
#   2 - Critical issues found

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPORTS_DIR="reports"
MIN_QUERIES=5
MIN_TOKENS=1000
MAX_TOKENS=1000000
MIN_DIVERSITY=0.3  # 30% unique queries
SESSION_TYPE="baseline"
FIX_MODE=false
VERBOSE=false

# Counters
TOTAL_SESSIONS=0
PASSED_SESSIONS=0
WARNING_SESSIONS=0
FAILED_SESSIONS=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --baseline)
            SESSION_TYPE="baseline"
            shift
            ;;
        --optimized)
            SESSION_TYPE="optimized"
            shift
            ;;
        --fix)
            FIX_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--baseline|--optimized] [--fix] [--verbose]"
            echo ""
            echo "Validates session quality and provides actionable feedback."
            echo ""
            echo "Options:"
            echo "  --baseline    Validate baseline sessions (default)"
            echo "  --optimized   Validate optimized sessions"
            echo "  --fix         Attempt to fix common issues"
            echo "  --verbose     Show detailed validation output"
            echo "  -h, --help    Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo "  $1"
    fi
}

# Validate JSON structure
validate_json_structure() {
    local file=$1
    local required_fields=("total_queries" "total_tokens" "timestamp")
    
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$file" > /dev/null 2>&1; then
            log_error "Missing required field: $field"
            return 1
        fi
    done
    
    return 0
}

# Check query count
check_query_count() {
    local file=$1
    local query_count=$(jq -r '.total_queries // 0' "$file")
    
    if [ "$query_count" -lt "$MIN_QUERIES" ]; then
        log_warning "Low query count: $query_count (minimum: $MIN_QUERIES)"
        log_verbose "Recommendation: Run longer sessions with more queries"
        return 1
    fi
    
    log_verbose "Query count: $query_count ✓"
    return 0
}

# Check token count
check_token_count() {
    local file=$1
    local token_count=$(jq -r '.total_tokens // 0' "$file")
    
    if [ "$token_count" -lt "$MIN_TOKENS" ]; then
        log_warning "Low token count: $token_count (minimum: $MIN_TOKENS)"
        log_verbose "Recommendation: Use more complex queries"
        return 1
    fi
    
    if [ "$token_count" -gt "$MAX_TOKENS" ]; then
        log_warning "Unusually high token count: $token_count"
        log_verbose "This may indicate an outlier session"
        return 1
    fi
    
    log_verbose "Token count: $token_count ✓"
    return 0
}

# Check query diversity
check_query_diversity() {
    local file=$1
    
    # Extract queries if available
    if ! jq -e '.queries' "$file" > /dev/null 2>&1; then
        log_verbose "No query details available, skipping diversity check"
        return 0
    fi
    
    local total_queries=$(jq -r '.queries | length' "$file")
    local unique_queries=$(jq -r '.queries | unique | length' "$file")
    
    if [ "$total_queries" -eq 0 ]; then
        return 0
    fi
    
    local diversity=$(echo "scale=2; $unique_queries / $total_queries" | bc)
    local min_diversity_int=$(echo "$MIN_DIVERSITY * 100" | bc | cut -d. -f1)
    local diversity_int=$(echo "$diversity * 100" | bc | cut -d. -f1)
    
    if [ "$diversity_int" -lt "$min_diversity_int" ]; then
        log_warning "Low query diversity: ${diversity_int}% unique (minimum: ${min_diversity_int}%)"
        log_verbose "Recommendation: Use more varied queries"
        return 1
    fi
    
    log_verbose "Query diversity: ${diversity_int}% ✓"
    return 0
}

# Check timestamp validity
check_timestamp() {
    local file=$1
    local timestamp=$(jq -r '.timestamp // ""' "$file")
    
    if [ -z "$timestamp" ]; then
        log_warning "Missing timestamp"
        return 1
    fi
    
    # Check if timestamp is recent (within last 30 days)
    local current_time=$(date +%s)
    local session_time=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${timestamp%.*}" +%s 2>/dev/null || echo 0)
    local age_days=$(( (current_time - session_time) / 86400 ))
    
    if [ "$age_days" -gt 30 ]; then
        log_warning "Old session: $age_days days old"
        log_verbose "Consider collecting fresh data"
        return 1
    fi
    
    log_verbose "Timestamp: $timestamp ✓"
    return 0
}

# Check for outliers
check_outliers() {
    local file=$1
    local token_count=$(jq -r '.total_tokens // 0' "$file")
    local query_count=$(jq -r '.total_queries // 0' "$file")
    
    if [ "$query_count" -eq 0 ]; then
        return 0
    fi
    
    local tokens_per_query=$(( token_count / query_count ))
    
    # Flag if tokens per query is unusually high or low
    if [ "$tokens_per_query" -lt 100 ]; then
        log_warning "Unusually low tokens per query: $tokens_per_query"
        log_verbose "This may indicate very simple queries"
        return 1
    fi
    
    if [ "$tokens_per_query" -gt 10000 ]; then
        log_warning "Unusually high tokens per query: $tokens_per_query"
        log_verbose "This may indicate very complex queries or errors"
        return 1
    fi
    
    log_verbose "Tokens per query: $tokens_per_query ✓"
    return 0
}

# Validate a single session file
validate_session() {
    local file=$1
    local filename=$(basename "$file")
    local issues=0
    local warnings=0
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Validating: $filename"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check JSON structure
    if ! validate_json_structure "$file"; then
        ((issues++))
        log_error "Invalid JSON structure"
        return 2
    fi
    
    # Run all checks
    check_query_count "$file" || ((warnings++))
    check_token_count "$file" || ((warnings++))
    check_query_diversity "$file" || ((warnings++))
    check_timestamp "$file" || ((warnings++))
    check_outliers "$file" || ((warnings++))
    
    # Summary for this session
    if [ "$issues" -gt 0 ]; then
        log_error "FAILED: $issues critical issues"
        return 2
    elif [ "$warnings" -gt 0 ]; then
        log_warning "PASSED WITH WARNINGS: $warnings warnings"
        return 1
    else
        log_success "PASSED: All checks passed"
        return 0
    fi
}

# Generate quality report
generate_report() {
    local report_file="$REPORTS_DIR/quality_report_${SESSION_TYPE}_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "SESSION QUALITY VALIDATION REPORT"
        echo "=================================="
        echo ""
        echo "Session Type: $SESSION_TYPE"
        echo "Validation Date: $(date)"
        echo ""
        echo "SUMMARY"
        echo "-------"
        echo "Total Sessions: $TOTAL_SESSIONS"
        echo "Passed: $PASSED_SESSIONS ($(( PASSED_SESSIONS * 100 / TOTAL_SESSIONS ))%)"
        echo "Warnings: $WARNING_SESSIONS ($(( WARNING_SESSIONS * 100 / TOTAL_SESSIONS ))%)"
        echo "Failed: $FAILED_SESSIONS ($(( FAILED_SESSIONS * 100 / TOTAL_SESSIONS ))%)"
        echo ""
        echo "QUALITY CRITERIA"
        echo "----------------"
        echo "Minimum Queries: $MIN_QUERIES"
        echo "Minimum Tokens: $MIN_TOKENS"
        echo "Maximum Tokens: $MAX_TOKENS"
        echo "Minimum Diversity: $(echo "$MIN_DIVERSITY * 100" | bc)%"
        echo ""
        echo "RECOMMENDATIONS"
        echo "---------------"
        
        if [ "$FAILED_SESSIONS" -gt 0 ]; then
            echo "- Review and fix failed sessions"
            echo "- Ensure all required fields are present"
        fi
        
        if [ "$WARNING_SESSIONS" -gt 0 ]; then
            echo "- Consider re-running sessions with warnings"
            echo "- Aim for more queries per session (5+)"
            echo "- Use more varied and complex queries"
        fi
        
        if [ "$PASSED_SESSIONS" -eq "$TOTAL_SESSIONS" ]; then
            echo "- All sessions passed! Ready for analysis"
        fi
        
    } > "$report_file"
    
    log_success "Quality report saved to: $report_file"
}

# Main validation logic
main() {
    echo "╔════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                      SESSION QUALITY VALIDATOR                                 ║"
    echo "╚════════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    log_info "Session Type: $SESSION_TYPE"
    log_info "Reports Directory: $REPORTS_DIR"
    log_info "Fix Mode: $FIX_MODE"
    echo ""
    
    # Check if reports directory exists
    if [ ! -d "$REPORTS_DIR" ]; then
        log_error "Reports directory not found: $REPORTS_DIR"
        exit 2
    fi
    
    # Find session files
    local pattern="*${SESSION_TYPE}*.json"
    local files=("$REPORTS_DIR"/$pattern)
    
    if [ ! -e "${files[0]}" ]; then
        log_warning "No session files found matching: $pattern"
        exit 0
    fi
    
    # Validate each session
    for file in "${files[@]}"; do
        ((TOTAL_SESSIONS++))
        
        validate_session "$file"
        local result=$?
        
        case $result in
            0)
                ((PASSED_SESSIONS++))
                ;;
            1)
                ((WARNING_SESSIONS++))
                ;;
            2)
                ((FAILED_SESSIONS++))
                ;;
        esac
    done
    
    # Final summary
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                           VALIDATION SUMMARY                                   ║"
    echo "╚════════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Total Sessions:    $TOTAL_SESSIONS"
    echo "Passed:            $PASSED_SESSIONS ($(( PASSED_SESSIONS * 100 / TOTAL_SESSIONS ))%)"
    echo "Warnings:          $WARNING_SESSIONS ($(( WARNING_SESSIONS * 100 / TOTAL_SESSIONS ))%)"
    echo "Failed:            $FAILED_SESSIONS ($(( FAILED_SESSIONS * 100 / TOTAL_SESSIONS ))%)"
    echo ""
    
    # Generate report
    generate_report
    
    # Exit with appropriate code
    if [ "$FAILED_SESSIONS" -gt 0 ]; then
        log_error "Validation failed: $FAILED_SESSIONS sessions have critical issues"
        exit 2
    elif [ "$WARNING_SESSIONS" -gt 0 ]; then
        log_warning "Validation passed with warnings: $WARNING_SESSIONS sessions need attention"
        exit 1
    else
        log_success "All sessions passed validation!"
        exit 0
    fi
}

# Run main function
main
