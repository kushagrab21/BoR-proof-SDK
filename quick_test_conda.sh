#!/bin/bash
# Quick test using conda Python (bypasses venv issues)

export PATH="/opt/anaconda3/bin:$PATH"
exec make clean test-system

