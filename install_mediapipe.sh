#!/bin/bash
set -e

echo "Checking Python version..."
python --version

echo "Checking pip version..."
python -m pip --version

echo "Checking network connectivity..."
curl -I https://pypi.org/simple/mediapipe/ || echo "Network check failed"

echo "Installing MediaPipe..."
python -m pip install mediapipe --verbose --no-cache-dir || {
    echo "Standard install failed, trying with --no-binary..."
    python -m pip install mediapipe --no-binary :all: --verbose || {
        echo "All installation methods failed"
        exit 1
    }
}

echo "Verifying MediaPipe installation..."
python -c "import mediapipe; print(f'MediaPipe version: {mediapipe.__version__}')"

