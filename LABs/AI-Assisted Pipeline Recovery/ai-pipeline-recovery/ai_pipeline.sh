#!/bin/bash
#
# ai_pipeline.sh - Main orchestrator for AI-assisted pipeline recovery
#
# Features:
#   - Execute pipeline steps sequentially
#   - Capture stdout, stderr, exit code for each step
#   - On failure, invoke AI recovery
#   - Track retry count (max 3 attempts)
#   - Log all recovery actions for audit
#   - Support dry-run mode (show fix, don't apply)

set -o pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAX_RETRIES=${MAX_RETRIES:-3}
DRY_RUN=${DRY_RUN:-false}
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/pipeline_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure log directory exists
mkdir -p "$LOG_DIR"

#######################################
# Log a message to both console and file
# Arguments:
#   $1 - Log level (INFO, WARN, ERROR, SUCCESS)
#   $2 - Message
#######################################
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local color=""

    case "$level" in
        INFO)    color="$BLUE" ;;
        WARN)    color="$YELLOW" ;;
        ERROR)   color="$RED" ;;
        SUCCESS) color="$GREEN" ;;
        *)       color="$NC" ;;
    esac

    # Console output with color
    echo -e "${color}[$timestamp] [$level] $message${NC}"

    # File output without color
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

#######################################
# Log JSON-formatted entry for parsing
# Arguments:
#   $1 - Step name
#   $2 - Status
#   $3 - Error message (optional)
#   $4 - AI suggestion (optional)
#   $5 - Action taken (optional)
#######################################
log_json() {
    local step="$1"
    local status="$2"
    local error="${3:-}"
    local ai_suggestion="${4:-}"
    local action="${5:-}"
    local timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

    # Escape special characters for JSON
    error=$(echo "$error" | sed 's/"/\\"/g' | tr '\n' ' ')
    ai_suggestion=$(echo "$ai_suggestion" | sed 's/"/\\"/g' | tr '\n' ' ')
    action=$(echo "$action" | sed 's/"/\\"/g' | tr '\n' ' ')

    local json_entry=$(cat <<EOF
{"timestamp":"$timestamp","step":"$step","status":"$status","error":"$error","ai_suggestion":"$ai_suggestion","action":"$action"}
EOF
)
    echo "$json_entry" >> "${LOG_DIR}/pipeline_audit.jsonl"
}

#######################################
# Execute a pipeline step with retry logic
# Arguments:
#   $1 - Step name
#   $2 - Command to execute
#   $3 - Working directory (optional)
# Returns:
#   0 on success, 1 on failure after all retries
#######################################
run_step() {
    local step_name="$1"
    local command="$2"
    local work_dir="${3:-$SCRIPT_DIR}"
    local attempt=1
    local exit_code=0
    local stdout_file=$(mktemp)
    local stderr_file=$(mktemp)

    log "INFO" "Starting step: $step_name"
    log "INFO" "Command: $command"

    while [ $attempt -le $MAX_RETRIES ]; do
        log "INFO" "Attempt $attempt of $MAX_RETRIES"

        # Execute command and capture output
        cd "$work_dir"
        eval "$command" > "$stdout_file" 2> "$stderr_file"
        exit_code=$?

        if [ $exit_code -eq 0 ]; then
            log "SUCCESS" "Step '$step_name' completed successfully"
            log_json "$step_name" "success"

            # Show stdout if any
            if [ -s "$stdout_file" ]; then
                log "INFO" "Output:"
                cat "$stdout_file"
            fi

            rm -f "$stdout_file" "$stderr_file"
            return 0
        fi

        # Step failed
        local error_output=$(cat "$stderr_file")
        log "ERROR" "Step '$step_name' failed with exit code $exit_code"
        log "ERROR" "Error output: $error_output"

        # Check if we have retries left
        if [ $attempt -ge $MAX_RETRIES ]; then
            log "ERROR" "Max retries ($MAX_RETRIES) reached for step '$step_name'"
            log_json "$step_name" "failed" "$error_output" "" "max_retries_reached"
            rm -f "$stdout_file" "$stderr_file"
            return 1
        fi

        # Attempt AI recovery
        log "INFO" "Invoking AI recovery..."

        local ai_suggestion=""
        local recovery_action=""

        if ai_suggestion=$("$SCRIPT_DIR/ai_recover.sh" \
            --step "$step_name" \
            --command "$command" \
            --error "$error_output" \
            --exit-code "$exit_code" \
            --work-dir "$work_dir" \
            2>&1); then

            log "INFO" "AI suggestion received:"
            echo "$ai_suggestion"

            if [ "$DRY_RUN" = "true" ]; then
                log "WARN" "Dry-run mode: Not applying fix"
                log_json "$step_name" "dry_run" "$error_output" "$ai_suggestion" "skipped"
                rm -f "$stdout_file" "$stderr_file"
                return 1
            fi

            # Extract and apply the fix from AI response
            recovery_action=$(echo "$ai_suggestion" | grep -A 100 "^FIX:" | tail -n +2)

            if [ -n "$recovery_action" ]; then
                log "INFO" "Applying recovery action..."
                log "INFO" "Action: $recovery_action"

                # Execute the recovery action
                if eval "$recovery_action" 2>&1; then
                    log "SUCCESS" "Recovery action applied successfully"
                    log_json "$step_name" "recovered" "$error_output" "$ai_suggestion" "$recovery_action"
                else
                    log "ERROR" "Recovery action failed"
                    log_json "$step_name" "recovery_failed" "$error_output" "$ai_suggestion" "$recovery_action"
                fi
            else
                log "WARN" "No actionable fix found in AI response"
                log_json "$step_name" "no_fix" "$error_output" "$ai_suggestion" ""
            fi
        else
            log "ERROR" "AI recovery failed: $ai_suggestion"
            log_json "$step_name" "ai_error" "$error_output" "" "ai_recovery_failed"
        fi

        ((attempt++))
        log "INFO" "Retrying step..."
        sleep 1
    done

    rm -f "$stdout_file" "$stderr_file"
    return 1
}

#######################################
# Run a pipeline from a definition file
# Arguments:
#   $1 - Pipeline definition file (one command per line)
#######################################
run_pipeline() {
    local pipeline_file="$1"
    local overall_status=0
    local step_num=0

    if [ ! -f "$pipeline_file" ]; then
        log "ERROR" "Pipeline file not found: $pipeline_file"
        return 1
    fi

    log "INFO" "=========================================="
    log "INFO" "Starting pipeline: $pipeline_file"
    log "INFO" "Max retries: $MAX_RETRIES"
    log "INFO" "Dry-run: $DRY_RUN"
    log "INFO" "Log file: $LOG_FILE"
    log "INFO" "=========================================="

    while IFS= read -r line || [ -n "$line" ]; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

        ((step_num++))
        local step_name="step_${step_num}"

        # Check for custom step name (format: "name: command")
        if [[ "$line" =~ ^([^:]+):(.+)$ ]]; then
            step_name="${BASH_REMATCH[1]}"
            line="${BASH_REMATCH[2]}"
        fi

        # Trim whitespace
        step_name=$(echo "$step_name" | xargs)
        line=$(echo "$line" | xargs)

        if ! run_step "$step_name" "$line"; then
            log "ERROR" "Pipeline failed at step: $step_name"
            overall_status=1
            break
        fi
    done < "$pipeline_file"

    if [ $overall_status -eq 0 ]; then
        log "SUCCESS" "=========================================="
        log "SUCCESS" "Pipeline completed successfully!"
        log "SUCCESS" "=========================================="
    else
        log "ERROR" "=========================================="
        log "ERROR" "Pipeline failed!"
        log "ERROR" "=========================================="
    fi

    return $overall_status
}

#######################################
# Print usage information
#######################################
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] <pipeline_file | command>

AI-Assisted Pipeline Recovery - Execute commands with automatic error recovery

OPTIONS:
    -h, --help          Show this help message
    -d, --dry-run       Show AI suggestions but don't apply fixes
    -r, --retries NUM   Maximum retry attempts (default: 3)
    -s, --step NAME     Run a single command with given step name
    -v, --verbose       Enable verbose output

EXAMPLES:
    # Run a pipeline file
    $(basename "$0") pipeline.txt

    # Run with dry-run mode
    $(basename "$0") --dry-run pipeline.txt

    # Run a single command
    $(basename "$0") --step "process_data" "python data_processor.py input.csv"

    # Run with custom retry count
    $(basename "$0") --retries 5 pipeline.txt

PIPELINE FILE FORMAT:
    # Comments start with #
    step_name: command to execute
    another_step: another command

    # Or just commands (auto-numbered as step_1, step_2, etc.)
    python script.py
    ./process.sh

EOF
}

#######################################
# Main entry point
#######################################
main() {
    local single_step=""
    local single_command=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -r|--retries)
                MAX_RETRIES="$2"
                shift 2
                ;;
            -s|--step)
                single_step="$2"
                shift 2
                ;;
            -v|--verbose)
                set -x
                shift
                ;;
            -*)
                log "ERROR" "Unknown option: $1"
                usage
                exit 1
                ;;
            *)
                break
                ;;
        esac
    done

    # Check for remaining arguments
    if [ $# -eq 0 ]; then
        log "ERROR" "No pipeline file or command specified"
        usage
        exit 1
    fi

    # Single step mode
    if [ -n "$single_step" ]; then
        single_command="$*"
        run_step "$single_step" "$single_command"
        exit $?
    fi

    # Pipeline mode
    local pipeline_file="$1"
    run_pipeline "$pipeline_file"
    exit $?
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
