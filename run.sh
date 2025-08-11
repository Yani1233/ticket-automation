#!/bin/bash

# Simple run script for Coolie Ticket Monitor

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

clear

echo -e "${GREEN}=========================================="
echo -e "🎬 COOLIE TICKET MONITOR"
echo -e "==========================================${NC}"

# Quick checks
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Setting up virtual environment...${NC}"
    python3 -m venv .venv
    .venv/bin/pip install -q -r requirements.txt
    echo -e "${GREEN}✅ Setup complete${NC}"
fi

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ ERROR: .env file not found!${NC}"
    echo "Please configure your settings first."
    exit 1
fi

# Run the monitor
.venv/bin/python3 main.py