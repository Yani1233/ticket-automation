#!/bin/bash

# Ticket Alert Runner Script

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎬 Ticket Alert System${NC}"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -e .

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${GREEN}Loading environment variables...${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${RED}Warning: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your credentials."
    exit 1
fi

# Run the alert system
echo -e "${GREEN}Starting ticket monitoring...${NC}"
echo ""

# Pass all arguments to the CLI
python -m ticket_alert.cli "$@"