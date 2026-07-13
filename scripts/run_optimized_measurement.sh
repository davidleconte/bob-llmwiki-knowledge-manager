#!/bin/bash
#
# Optimized Measurement Script
#
# Automates the process of running optimized measurements for Phase 3 validation.
# This script helps collect 20+ Bob Shell sessions WITH optimization enabled to
# measure actual token savings.
#
# Usage:
#   ./scripts/run_optimized_measurement.sh [num_sessions]
#
# Example:
#   ./scripts/run_optimized_measurement.sh 20
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$PROJECT_ROOT/evaluation/data/sessions"
EXAMPLES_DIR="$PROJECT_ROOT/examples"

# Default number of sessions
NUM_SESSIONS="${1:-20}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"

# Print header
echo ""
echo "========================================================================"
echo "  OPTIMIZED MEASUREMENT SCRIPT"
echo "========================================================================"
echo ""
echo "This script will guide you through collecting optimized measurements"
echo "for Phase 3 validation. You will run $NUM_SESSIONS Bob Shell sessions"
echo "WITH optimization enabled to measure actual token savings."
echo ""
echo "Data will be saved to: $DATA_DIR"
echo ""
echo "========================================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is required but not found"
    exit 1
fi

# Check if session tracker exists
if [ ! -f "$EXAMPLES_DIR/bob_shell_session_tracker.py" ]; then
    log_error "Session tracker not found: $EXAMPLES_DIR/bob_shell_session_tracker.py"
    exit 1
fi

# Check if baseline sessions exist
baseline_list="$DATA_DIR/baseline_sessions.txt"
if [ ! -f "$baseline_list" ]; then
    log_warning "No baseline sessions found at: $baseline_list"
    echo ""
    echo "It's recommended to run baseline measurements first:"
    echo "  ./scripts/run_baseline_measurement.sh"
    echo ""
    read -p "Continue anyway? (y/n): " response
    if [[ ! "$response" =~ ^[Yy] ]]; then
        log_info "Cancelled by user"
        exit 0
    fi
fi

log_info "Starting optimized measurement collection..."
echo ""

# Instructions
echo "INSTRUCTIONS:"
echo "-------------"
echo "1. For each session, you'll be prompted to start tracking"
echo "2. Use Bob Shell normally for your tasks (optimization is ENABLED)"
echo "3. Enter queries and responses as prompted"
echo "4. Type 'done' when the session is complete"
echo "5. Repeat for $NUM_SESSIONS sessions"
echo ""
echo "TIP: Try to use similar queries to your baseline sessions for comparison"
echo ""
echo "OPTIMIZATION FEATURES ENABLED:"
echo "  ✓ Response caching (exact match)"
echo "  ✓ Semantic caching (similar queries)"
echo "  ✓ Prompt optimization (redundancy removal)"
echo "  ✓ Context truncation (smart relevance-based)"
echo ""

read -p "Press Enter to start, or Ctrl+C to cancel..."
echo ""

# Counter for completed sessions
completed=0
session_ids=()

# Main loop
for i in $(seq 1 $NUM_SESSIONS); do
    session_id="optimized_$(date +%Y%m%d)_$(printf "%03d" $i)"
    
    log_info "Session $i of $NUM_SESSIONS: $session_id"
    echo ""
    
    # Ask if user wants to run this session
    read -p "Start session $i? (y/n/skip): " response
    
    case "$response" in
        [Yy]* )
            # Run session tracker with optimization enabled
            log_info "Starting session tracker (optimization ENABLED)..."
            python3 "$EXAMPLES_DIR/bob_shell_session_tracker.py" \
                --mode optimized \
                --session-id "$session_id"
            
            if [ $? -eq 0 ]; then
                completed=$((completed + 1))
                session_ids+=("$session_id")
                log_success "Session $session_id completed"
            else
                log_error "Session $session_id failed"
            fi
            ;;
        [Ss]* )
            log_warning "Skipping session $i"
            ;;
        * )
            log_warning "Cancelled by user"
            break
            ;;
    esac
    
    echo ""
    echo "Progress: $completed/$NUM_SESSIONS sessions completed"
    echo ""
    
    # Ask if user wants to continue
    if [ $i -lt $NUM_SESSIONS ]; then
        read -p "Continue to next session? (y/n): " continue_response
        if [[ ! "$continue_response" =~ ^[Yy] ]]; then
            log_info "Stopping measurement collection"
            break
        fi
    fi
    
    echo ""
done

# Summary
echo ""
echo "========================================================================"
echo "  OPTIMIZED MEASUREMENT SUMMARY"
echo "========================================================================"
echo ""
echo "Completed Sessions: $completed"
echo "Target Sessions:    $NUM_SESSIONS"
echo ""

if [ $completed -gt 0 ]; then
    echo "Session IDs:"
    for sid in "${session_ids[@]}"; do
        echo "  - $sid"
    done
    echo ""
    
    # Save session list
    list_file="$DATA_DIR/optimized_sessions.txt"
    printf "%s\n" "${session_ids[@]}" > "$list_file"
    log_success "Session list saved to: $list_file"
    echo ""
    
    # Calculate progress
    progress=$((completed * 100 / NUM_SESSIONS))
    echo "Progress: $progress%"
    echo ""
    
    if [ $completed -ge $NUM_SESSIONS ]; then
        log_success "Optimized measurement collection COMPLETE!"
        echo ""
        echo "Next steps:"
        echo "1. Review the collected data in: $DATA_DIR"
        
        # Check if we can run analysis
        if [ -f "$baseline_list" ]; then
            echo "2. Run analysis to compare baseline vs optimized:"
            echo ""
            echo "   python3 examples/bob_shell_session_tracker.py --analyze \\"
            echo "     --baseline-sessions \$(cat $baseline_list | tr '\n' ' ') \\"
            echo "     --optimized-sessions \$(cat $list_file | tr '\n' ' ')"
            echo ""
        else
            echo "2. Collect baseline measurements if not done yet"
            echo "3. Then run analysis to compare results"
        fi
    else
        log_warning "Optimized measurement collection INCOMPLETE"
        echo ""
        echo "You collected $completed out of $NUM_SESSIONS sessions."
        echo "Run this script again to collect more sessions."
    fi
else
    log_error "No sessions completed"
fi

echo ""
echo "========================================================================"
echo ""
