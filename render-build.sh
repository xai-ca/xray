#!/bin/bash
set -e  # Exit on first error

echo "Updating and installing dependencies..."
sudo apt-get update
sudo apt-get install -y graphviz  # Install Graphviz

echo "Installing Python dependencies..."
pip install -r requirements.txt  # Install Python dependencies

echo "Build process complete."
