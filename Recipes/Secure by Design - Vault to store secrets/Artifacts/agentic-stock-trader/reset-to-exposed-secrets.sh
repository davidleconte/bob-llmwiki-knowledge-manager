#!/bin/bash

# Reset script for Vault demonstration
# This script helps you revert to the version with exposed secrets

set -e

BACKUP_FILE="AgenticStockTrader.java.exposed-secrets"
ORIGINAL_FILE="src/main/java/com/demo/stocktrader/AgenticStockTrader.java"

echo "======================================"
echo "Agentic Stock Trader - Demo Reset"
echo "======================================"
echo ""

# Function to create backup of exposed secrets version
create_backup() {
    if [ ! -f "$BACKUP_FILE" ]; then
        echo "Creating backup of exposed secrets version..."
        cp "$ORIGINAL_FILE" "$BACKUP_FILE"
        echo "✓ Backup created: $BACKUP_FILE"
    else
        echo "✓ Backup already exists: $BACKUP_FILE"
    fi
}

# Function to restore from backup
restore_from_backup() {
    if [ -f "$BACKUP_FILE" ]; then
        echo "Restoring exposed secrets version from backup..."
        cp "$BACKUP_FILE" "$ORIGINAL_FILE"
        echo "✓ Restored: $ORIGINAL_FILE"
        echo ""
        echo "The application now contains EXPOSED SECRETS again."
        echo "You'll need to rebuild the container:"
        echo "  ./build.sh"
    else
        echo "ERROR: Backup file not found: $BACKUP_FILE"
        echo "Cannot restore. Please ensure you've run this script with 'backup' first."
        exit 1
    fi
}

# Function to show current status
show_status() {
    echo "Current status:"
    echo ""
    if [ -f "$BACKUP_FILE" ]; then
        echo "✓ Backup exists: $BACKUP_FILE"
    else
        echo "✗ No backup found"
    fi
    echo ""
    if [ -f "$ORIGINAL_FILE" ]; then
        echo "✓ Source file exists: $ORIGINAL_FILE"
        echo ""
        # Check if file contains hardcoded secrets
        if grep -q "ALPHA_VANTAGE_API_KEY = \"AV_DEMO_KEY" "$ORIGINAL_FILE" 2>/dev/null; then
            echo "Status: File contains EXPOSED SECRETS"
        else
            echo "Status: File appears to be modified (secrets may be removed/vaulted)"
        fi
    else
        echo "✗ Source file not found: $ORIGINAL_FILE"
    fi
}

# Main script logic
case "${1:-}" in
    backup)
        create_backup
        ;;
    restore)
        restore_from_backup
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {backup|restore|status}"
        echo ""
        echo "Commands:"
        echo "  backup  - Create a backup of the current exposed secrets version"
        echo "  restore - Restore the exposed secrets version from backup"
        echo "  status  - Show current backup and file status"
        echo ""
        echo "Typical workflow:"
        echo "  1. Run './reset-to-exposed-secrets.sh backup' BEFORE modifying code"
        echo "  2. Demonstrate Vault integration (modify code to use Vault)"
        echo "  3. Run './reset-to-exposed-secrets.sh restore' to reset for next demo"
        echo "  4. Run './build.sh' to rebuild with exposed secrets"
        echo ""
        exit 1
        ;;
esac

echo ""
echo "======================================"

# Made with Bob
