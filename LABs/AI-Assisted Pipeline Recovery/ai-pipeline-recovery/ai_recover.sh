#!/bin/bash
#
# ai_recover.sh - AI-powered recovery module using IBM Bob CLI
#
# Features:
#   - Format error context for bob-cli
#   - Parse AI response for actionable fix
#   - Validate fix is safe to apply
#   - Return structured response for pipeline

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="${SCRIPT_DIR}/prompts"

# Configuration
BOB_TIMEOUT=${BOB_TIMEOUT:-60}
MAX_CONTEXT_LINES=${MAX_CONTEXT_LINES:-50}

# Blocked commands for safety
BLOCKED_PATTERNS=(
    "rm -rf /"
    "rm -rf /*"
    "rm -rf ~"
    "mkfs"
    "dd if="
    ":(){:|:&};:"
    "> /dev/sd"
    "chmod -R 777 /"
    "chown -R"
    "curl.*| *sh"
    "wget.*| *sh"
)

#######################################
# Check if a command is safe to execute
# Arguments:
#   $1 - Command to validate
# Returns:
#   0 if safe, 1 if blocked
#######################################
is_safe_command() {
    local cmd="$1"

    for pattern in "${BLOCKED_PATTERNS[@]}"; do
        if [[ "$cmd" == *"$pattern"* ]]; then
            echo "BLOCKED: Command matches dangerous pattern: $pattern" >&2
            return 1
        fi
    done

    return 0
}

#######################################
# Get relevant context for the error
# Arguments:
#   $1 - Working directory
#   $2 - Command that failed
# Returns:
#   Context information (file listings, etc.)
#######################################
gather_context() {
    local work_dir="$1"
    local command="$2"
    local context=""

    # List files in working directory
    context+="=== Directory contents ===\n"
    context+=$(ls -la "$work_dir" 2>/dev/null | head -20)
    context+="\n\n"

    # If command involves a specific file, show its contents/info
    local file_pattern='([^ ]+\.(py|sh|csv|json|txt|yaml|yml))'
    if [[ "$command" =~ $file_pattern ]]; then
        local file="${BASH_REMATCH[1]}"
        if [ -f "$work_dir/$file" ]; then
            context+="=== Contents of $file (first $MAX_CONTEXT_LINES lines) ===\n"
            context+=$(head -n "$MAX_CONTEXT_LINES" "$work_dir/$file" 2>/dev/null)
            context+="\n\n"
        fi
    fi

    # Check for data files mentioned in error
    for ext in csv json; do
        local data_files=$(find "$work_dir" -maxdepth 1 -name "*.$ext" 2>/dev/null | head -5)
        if [ -n "$data_files" ]; then
            for f in $data_files; do
                context+="=== Sample from $(basename "$f") (first 10 lines) ===\n"
                context+=$(head -n 10 "$f" 2>/dev/null)
                context+="\n\n"
            done
        fi
    done

    echo -e "$context"
}

#######################################
# Detect error type and select prompt template
# Arguments:
#   $1 - Error message
# Returns:
#   Prompt template name
#######################################
detect_error_type() {
    local error="$1"

    # Data-related errors
    if [[ "$error" == *"KeyError"* ]] || \
       [[ "$error" == *"column"* ]] || \
       [[ "$error" == *"schema"* ]] || \
       [[ "$error" == *"CSV"* ]] || \
       [[ "$error" == *"JSON"* ]]; then
        echo "data_error"
        return
    fi

    # Import/module errors
    if [[ "$error" == *"ImportError"* ]] || \
       [[ "$error" == *"ModuleNotFoundError"* ]] || \
       [[ "$error" == *"AttributeError"* ]] || \
       [[ "$error" == *"No module named"* ]]; then
        echo "import_error"
        return
    fi

    # Permission errors
    if [[ "$error" == *"Permission denied"* ]] || \
       [[ "$error" == *"PermissionError"* ]] || \
       [[ "$error" == *"EACCES"* ]]; then
        echo "permission_error"
        return
    fi

    # SQL/Database errors
    if [[ "$error" == *"SQL"* ]] || \
       [[ "$error" == *"sqlite"* ]] || \
       [[ "$error" == *"database"* ]] || \
       [[ "$error" == *"no such column"* ]]; then
        echo "sql_error"
        return
    fi

    # Config errors
    if [[ "$error" == *"config"* ]] || \
       [[ "$error" == *"YAML"* ]] || \
       [[ "$error" == *"yaml"* ]] || \
       [[ "$error" == *"missing key"* ]]; then
        echo "config_error"
        return
    fi

    # Default
    echo "general_error"
}

#######################################
# Load prompt template and fill placeholders
# Arguments:
#   $1 - Template name
#   $2 - Error message
#   $3 - Command
#   $4 - Context
# Returns:
#   Formatted prompt
#######################################
build_prompt() {
    local template_name="$1"
    local error="$2"
    local command="$3"
    local context="$4"

    local template_file="${PROMPTS_DIR}/${template_name}.txt"

    if [ -f "$template_file" ]; then
        # Load template and substitute placeholders
        local prompt=$(cat "$template_file")
        prompt="${prompt//\{\{ERROR\}\}/$error}"
        prompt="${prompt//\{\{COMMAND\}\}/$command}"
        prompt="${prompt//\{\{CONTEXT\}\}/$context}"
        echo "$prompt"
    else
        # Default prompt if no template found
        cat << EOF
I'm running an automated pipeline and encountered an error.

COMMAND: $command

ERROR:
$error

CONTEXT:
$context

Please analyze this error and suggest a fix. Your response MUST include:
1. Brief explanation of what went wrong
2. A concrete fix

Format your fix as:
FIX:
<single command or script to fix the issue>

The fix should be a shell command or short script that can be executed directly.
Only suggest safe operations (no destructive commands like rm -rf).
EOF
    fi
}

#######################################
# Call Bob CLI with the prompt
# Arguments:
#   $1 - Prompt text
# Returns:
#   AI response
#######################################
call_bob() {
    local prompt="$1"

    # Check if Bob CLI is available
    if ! command -v bob &> /dev/null; then
        echo "ERROR: bob CLI not found. Please install it first." >&2
        echo "See: https://internal.bob.ibm.com/docs/shell" >&2
        return 1
    fi

    # Find timeout command (gtimeout on macOS with coreutils, timeout on Linux)
    local timeout_cmd=""
    if command -v gtimeout &> /dev/null; then
        timeout_cmd="gtimeout"
    elif command -v timeout &> /dev/null; then
        timeout_cmd="timeout"
    fi

    # Call Bob with optional timeout
    local response
    if [ -n "$timeout_cmd" ]; then
        response=$(echo "$prompt" | $timeout_cmd "$BOB_TIMEOUT" bob 2>&1)
    else
        response=$(echo "$prompt" | bob 2>&1)
    fi
    local exit_code=$?

    if [ $exit_code -eq 124 ]; then
        echo "ERROR: Bob CLI timed out after ${BOB_TIMEOUT}s" >&2
        return 1
    elif [ $exit_code -ne 0 ]; then
        echo "ERROR: Bob CLI failed with exit code $exit_code" >&2
        echo "$response" >&2
        return 1
    fi

    echo "$response"
}

#######################################
# Extract fix command from AI response
# Arguments:
#   $1 - AI response
# Returns:
#   Fix command(s)
#######################################
extract_fix() {
    local response="$1"

    # Look for FIX: section
    local fix=""

    # Try to extract content after "FIX:" marker
    if echo "$response" | grep -q "^FIX:"; then
        fix=$(echo "$response" | sed -n '/^FIX:/,/^[A-Z]*:/p' | tail -n +2 | head -n -1)
        if [ -z "$fix" ]; then
            # If no next section, get everything after FIX:
            fix=$(echo "$response" | sed -n '/^FIX:/,$p' | tail -n +2)
        fi
    fi

    # Try code blocks if no FIX: marker
    if [ -z "$fix" ]; then
        fix=$(echo "$response" | sed -n '/```bash/,/```/p' | sed '1d;$d')
    fi
    if [ -z "$fix" ]; then
        fix=$(echo "$response" | sed -n '/```sh/,/```/p' | sed '1d;$d')
    fi
    if [ -z "$fix" ]; then
        fix=$(echo "$response" | sed -n '/```/,/```/p' | sed '1d;$d' | head -10)
    fi

    # Trim whitespace
    fix=$(echo "$fix" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    echo "$fix"
}

#######################################
# Main recovery function
#######################################
main() {
    local step=""
    local command=""
    local error=""
    local exit_code=""
    local work_dir="."

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --step)
                step="$2"
                shift 2
                ;;
            --command)
                command="$2"
                shift 2
                ;;
            --error)
                error="$2"
                shift 2
                ;;
            --exit-code)
                exit_code="$2"
                shift 2
                ;;
            --work-dir)
                work_dir="$2"
                shift 2
                ;;
            -h|--help)
                cat << EOF
Usage: $(basename "$0") [OPTIONS]

AI-powered error recovery using Bob CLI

OPTIONS:
    --step NAME       Step name that failed
    --command CMD     Command that failed
    --error MSG       Error message/output
    --exit-code NUM   Exit code of failed command
    --work-dir DIR    Working directory
    -h, --help        Show this help

OUTPUT:
    Prints analysis and fix suggestion. Fix is marked with "FIX:" prefix.
EOF
                exit 0
                ;;
            *)
                echo "Unknown option: $1" >&2
                exit 1
                ;;
        esac
    done

    # Validate required arguments
    if [ -z "$error" ]; then
        echo "ERROR: --error is required" >&2
        exit 1
    fi

    # Detect error type
    local error_type=$(detect_error_type "$error")
    echo "Detected error type: $error_type" >&2

    # Gather context
    local context=$(gather_context "$work_dir" "$command")

    # Build prompt
    local prompt=$(build_prompt "$error_type" "$error" "$command" "$context")

    echo "Calling Bob CLI for recovery suggestion..." >&2

    # Call Bob 
    local response
    if ! response=$(call_bob "$prompt"); then
        echo "Failed to get AI response" >&2
        exit 1
    fi

    # Extract fix
    local fix=$(extract_fix "$response")

    # Validate fix is safe
    if [ -n "$fix" ]; then
        if ! is_safe_command "$fix"; then
            echo "WARNING: AI suggested potentially dangerous command, blocking it" >&2
            fix=""
        fi
    fi

    # Output the response with fix clearly marked
    echo "=== AI Analysis ==="
    echo "$response"
    echo ""

    if [ -n "$fix" ]; then
        echo "FIX:"
        echo "$fix"
    else
        echo "NOTE: No actionable fix could be extracted from AI response"
    fi
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
