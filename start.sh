#!/bin/bash

# Coolie Ticket Monitor - Start Script
# This script starts the ticket monitoring system

echo "=========================================="
echo "🎬 COOLIE TICKET MONITOR - STARTUP"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
    
    echo "Installing dependencies..."
    .venv/bin/pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Configuration file (.env) not found!"
    echo "Please copy .env.template to .env and configure your settings."
    exit 1
fi

# Activate virtual environment and run
echo ""
echo "🚀 Starting monitors..."
echo ""

# Run the main monitor
.venv/bin/python3 main.py