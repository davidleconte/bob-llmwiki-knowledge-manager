#!/bin/bash

# Run script for Agentic Stock Trader
# This script runs the containerized application using Podman

set -e

echo "======================================"
echo "Running Agentic Stock Trader"
echo "======================================"

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo "ERROR: Podman is not installed!"
    echo "Please install Podman first: https://podman.io/getting-started/installation"
    exit 1
fi

# Check if image exists
if ! podman image exists agentic-stock-trader:latest; then
    echo "ERROR: Image 'agentic-stock-trader:latest' not found!"
    echo "Please build the image first:"
    echo "  ./build.sh"
    exit 1
fi

# Run the container with port mapping
echo ""
echo "Starting container..."
echo "Web UI will be available at: http://localhost:8080"
echo ""

podman run --rm --name agentic-stock-trader -p 8080:8080 agentic-stock-trader:latest

echo ""
echo "======================================"
echo "Container stopped!"
echo "======================================"

# Made with Bob
