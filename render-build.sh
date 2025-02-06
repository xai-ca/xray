#!/bin/bash
set -e  # Exit on first error

echo "Updating and installing dependencies..."
sudo apt-get update
sudo apt-get install -y graphviz

echo "Verifying Graphviz installation..."
which dot
dot -V  # Print version to confirm installation

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build process complete."
