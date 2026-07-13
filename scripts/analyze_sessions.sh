#!/bin/bash
#
# Analyze Sessions Script
# 
# Analyzes collected baseline and optimized sessions, generates reports and visualizations.
#
# Usage:
#   ./scripts/analyze_sessions.sh
#   ./scripts/analyze_sessions.sh --baseline-only
#   ./scripts/analyze_sessions.sh --optimized-only
#   ./scripts/analyze_sessions.sh --compare

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DATA_DIR="evaluation/data/sessions"
REPORTS_DIR="reports"
BASELINE_LIST="$DATA_DIR/baseline_sessions.txt"
OPTIMIZED_LIST="$DATA_DIR/optimized_sessions.txt"

# Print colored message
print_message() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Print section header
print_header() {
    echo ""
    echo "========================================================================"
    print_message "$BLUE" "  $1"
    echo "========================================================================"
    echo ""
}

# Check if session lists exist
check_session_lists() {
    local missing=0
    
    if [ ! -f "$BASELINE_LIST" ]; then
        print_message "$RED" "❌ Baseline session list not found: $BASELINE_LIST"
        print_message "$YELLOW" "   Run: ./scripts/run_baseline_measurement.sh"
        missing=1
    fi
    
    if [ ! -f "$OPTIMIZED_LIST" ]; then
        print_message "$RED" "❌ Optimized session list not found: $OPTIMIZED_LIST"
        print_message "$YELLOW" "   Run: ./scripts/run_optimized_measurement.sh"
        missing=1
    fi
    
    return $missing
}

# Load session IDs from file
load_session_ids() {
    local file=$1
    if [ -f "$file" ]; then
        cat "$file" | tr '\n' ' '
    fi
}

# Analyze baseline sessions
analyze_baseline() {
    print_header "ANALYZING BASELINE SESSIONS"
    
    if [ ! -f "$BASELINE_LIST" ]; then
        print_message "$RED" "❌ No baseline sessions found"
        return 1
    fi
    
    local baseline_ids=$(load_session_ids "$BASELINE_LIST")
    local count=$(echo "$baseline_ids" | wc -w | tr -d ' ')
    
    print_message "$GREEN" "Found $count baseline sessions"
    echo ""
    
    print_message "$BLUE" "Running analysis..."
    python3 examples/analysis_and_reporting.py \
        --analyze \
        --baseline $baseline_ids \
        --data-dir "$DATA_DIR"
    
    echo ""
    print_message "$GREEN" "✓ Baseline analysis complete"
}

# Analyze optimized sessions
analyze_optimized() {
    print_header "ANALYZING OPTIMIZED SESSIONS"
    
    if [ ! -f "$OPTIMIZED_LIST" ]; then
        print_message "$RED" "❌ No optimized sessions found"
        return 1
    fi
    
    local optimized_ids=$(load_session_ids "$OPTIMIZED_LIST")
    local count=$(echo "$optimized_ids" | wc -w | tr -d ' ')
    
    print_message "$GREEN" "Found $count optimized sessions"
    echo ""
    
    print_message "$BLUE" "Running analysis..."
    python3 examples/analysis_and_reporting.py \
        --analyze \
        --optimized $optimized_ids \
        --data-dir "$DATA_DIR"
    
    echo ""
    print_message "$GREEN" "✓ Optimized analysis complete"
}

# Compare baseline vs optimized
compare_sessions() {
    print_header "COMPARING BASELINE VS OPTIMIZED"
    
    if ! check_session_lists; then
        return 1
    fi
    
    local baseline_ids=$(load_session_ids "$BASELINE_LIST")
    local optimized_ids=$(load_session_ids "$OPTIMIZED_LIST")
    
    local baseline_count=$(echo "$baseline_ids" | wc -w | tr -d ' ')
    local optimized_count=$(echo "$optimized_ids" | wc -w | tr -d ' ')
    
    print_message "$GREEN" "Baseline sessions: $baseline_count"
    print_message "$GREEN" "Optimized sessions: $optimized_count"
    echo ""
    
    # Create reports directory
    mkdir -p "$REPORTS_DIR"
    
    # Generate text report
    print_message "$BLUE" "Generating text report..."
    python3 examples/analysis_and_reporting.py \
        --report \
        --baseline $baseline_ids \
        --optimized $optimized_ids \
        --format text \
        --output "$REPORTS_DIR/validation_report.txt" \
        --data-dir "$DATA_DIR"
    
    # Generate HTML report
    print_message "$BLUE" "Generating HTML report..."
    python3 examples/analysis_and_reporting.py \
        --report \
        --baseline $baseline_ids \
        --optimized $optimized_ids \
        --format html \
        --output "$REPORTS_DIR/validation_report.html" \
        --data-dir "$DATA_DIR"
    
    # Export CSV
    print_message "$BLUE" "Exporting CSV data..."
    python3 examples/analysis_and_reporting.py \
        --export \
        --baseline $baseline_ids \
        --optimized $optimized_ids \
        --format csv \
        --output "$REPORTS_DIR/sessions.csv" \
        --data-dir "$DATA_DIR"
    
    # Export JSON
    print_message "$BLUE" "Exporting JSON data..."
    python3 examples/analysis_and_reporting.py \
        --export \
        --baseline $baseline_ids \
        --optimized $optimized_ids \
        --format json \
        --output "$REPORTS_DIR/sessions.json" \
        --data-dir "$DATA_DIR"
    
    echo ""
    print_message "$GREEN" "✓ Comparison reports generated"
    print_message "$YELLOW" "  Reports saved to: $REPORTS_DIR/"
}

# Generate visualizations
generate_visualizations() {
    print_header "GENERATING VISUALIZATIONS"
    
    if ! check_session_lists; then
        return 1
    fi
    
    # Check if matplotlib is available
    if ! python3 -c "import matplotlib" 2>/dev/null; then
        print_message "$RED" "❌ matplotlib not installed"
        print_message "$YELLOW" "   Install with: pip install matplotlib"
        return 1
    fi
    
    local baseline_ids=$(load_session_ids "$BASELINE_LIST")
    local optimized_ids=$(load_session_ids "$OPTIMIZED_LIST")
    
    mkdir -p "$REPORTS_DIR"
    
    print_message "$BLUE" "Generating all visualizations..."
    python3 examples/visualization.py \
        --all \
        --baseline $baseline_ids \
        --optimized $optimized_ids \
        --output-dir "$REPORTS_DIR" \
        --data-dir "$DATA_DIR"
    
    echo ""
    print_message "$GREEN" "✓ Visualizations generated"
    print_message "$YELLOW" "  Charts saved to: $REPORTS_DIR/"
    echo ""
    print_message "$BLUE" "Generated files:"
    print_message "$BLUE" "  - savings_comparison.png"
    print_message "$BLUE" "  - cache_effectiveness.png"
    print_message "$BLUE" "  - latency_distribution.png"
    print_message "$BLUE" "  - savings_over_time.png"
    print_message "$BLUE" "  - dashboard.png"
}

# Full analysis pipeline
full_analysis() {
    print_header "FULL ANALYSIS PIPELINE"
    
    if ! check_session_lists; then
        return 1
    fi
    
    # Run all analyses
    analyze_baseline
    analyze_optimized
    compare_sessions
    generate_visualizations
    
    print_header "ANALYSIS COMPLETE"
    
    print_message "$GREEN" "✅ All analyses completed successfully!"
    echo ""
    print_message "$BLUE" "Generated files:"
    print_message "$BLUE" "  Reports:"
    print_message "$BLUE" "    - $REPORTS_DIR/validation_report.txt"
    print_message "$BLUE" "    - $REPORTS_DIR/validation_report.html"
    print_message "$BLUE" "    - $REPORTS_DIR/sessions.csv"
    print_message "$BLUE" "    - $REPORTS_DIR/sessions.json"
    print_message "$BLUE" "  Visualizations:"
    print_message "$BLUE" "    - $REPORTS_DIR/savings_comparison.png"
    print_message "$BLUE" "    - $REPORTS_DIR/cache_effectiveness.png"
    print_message "$BLUE" "    - $REPORTS_DIR/latency_distribution.png"
    print_message "$BLUE" "    - $REPORTS_DIR/savings_over_time.png"
    print_message "$BLUE" "    - $REPORTS_DIR/dashboard.png"
    echo ""
    print_message "$YELLOW" "Next steps:"
    print_message "$YELLOW" "  1. Review validation_report.html in your browser"
    print_message "$YELLOW" "  2. Check dashboard.png for visual summary"
    print_message "$YELLOW" "  3. Analyze detailed metrics in sessions.csv"
    echo ""
}

# Main script
main() {
    local mode="${1:-full}"
    
    case "$mode" in
        --baseline-only)
            analyze_baseline
            ;;
        --optimized-only)
            analyze_optimized
            ;;
        --compare)
            compare_sessions
            ;;
        --visualize)
            generate_visualizations
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  (no options)       Run full analysis pipeline"
            echo "  --baseline-only    Analyze baseline sessions only"
            echo "  --optimized-only   Analyze optimized sessions only"
            echo "  --compare          Compare baseline vs optimized"
            echo "  --visualize        Generate visualizations only"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Full analysis"
            echo "  $0 --compare          # Compare sessions"
            echo "  $0 --visualize        # Generate charts"
            ;;
        *)
            full_analysis
            ;;
    esac
}

# Run main
main "$@"
