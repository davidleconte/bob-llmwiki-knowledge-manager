#!/bin/bash

# Build script for Agentic Stock Trader
# This script builds the container image using Podman

set -e

echo "======================================"
echo "Building Agentic Stock Trader"
echo "======================================"

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo "ERROR: Podman is not installed!"
    echo "Please install Podman first: https://podman.io/getting-started/installation"
    exit 1
fi

# Build the image
echo ""
echo "Building container image..."
podman build -t agentic-stock-trader:latest .

echo ""
echo "======================================"
echo "Build complete!"
echo "======================================"
echo ""
echo "Image: agentic-stock-trader:latest"
echo ""
echo "To run the application:"
echo "  ./run.sh"
echo ""

# Made with Bob
