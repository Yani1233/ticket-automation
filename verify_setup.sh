#!/bin/bash

echo "🎬 BOOKMYSHOW MONITOR SETUP VERIFICATION"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "1. Python Installation:"
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python3 found:${NC} $(python3 --version)"
else
    echo -e "${RED}❌ Python3 not found${NC}"
fi

# Check required files
echo ""
echo "2. Monitor Scripts:"
monitors=(
    "bookmyshow_monitor.py"
    "bookmyshow_monitor_enhanced.py" 
    "bookmyshow_cloudscraper.py"
    "bookmyshow_selenium.py"
    "bookmyshow_proxy.py"
)

for monitor in "${monitors[@]}"; do
    if [ -f "$monitor" ]; then
        echo -e "${GREEN}✅ $monitor exists${NC}"
    else
        echo -e "${RED}❌ $monitor missing${NC}"
    fi
done

# Check GitHub workflows
echo ""
echo "3. GitHub Workflows:"
workflows=(
    ".github/workflows/ticket-monitor-simple.yml"
    ".github/workflows/ticket-monitor-multi.yml"
    ".github/workflows/test-monitors.yml"
)

for workflow in "${workflows[@]}"; do
    if [ -f "$workflow" ]; then
        echo -e "${GREEN}✅ $workflow exists${NC}"
    else
        echo -e "${RED}❌ $workflow missing${NC}"
    fi
done

# Verify target screens configuration
echo ""
echo "4. Target Screens Configuration:"
echo "   Checking that PVR Felicity Mall has been removed..."

felicity_count=$(grep -i "Felicity" bookmyshow_*.py 2>/dev/null | wc -l)
if [ "$felicity_count" -eq "0" ]; then
    echo -e "${GREEN}✅ PVR Felicity Mall successfully removed${NC}"
else
    echo -e "${RED}❌ PVR Felicity Mall still found in $felicity_count places${NC}"
fi

echo ""
echo "   Current target screens (should be 3):"
grep "PVR Soul Spirit" bookmyshow_monitor.py | head -1 | sed 's/^/   /'
grep "PVR Centro Mall" bookmyshow_monitor.py | head -1 | sed 's/^/   /'
grep "PVR Nexus Koramangala" bookmyshow_monitor.py | head -1 | sed 's/^/   /'

# Check environment variables
echo ""
echo "5. Email Configuration:"
if [ -n "$EMAIL_FROM" ]; then
    echo -e "${GREEN}✅ EMAIL_FROM is set${NC}"
else
    echo -e "${YELLOW}⚠️  EMAIL_FROM not set (needed for email alerts)${NC}"
fi

if [ -n "$EMAIL_TO" ]; then
    echo -e "${GREEN}✅ EMAIL_TO is set${NC}"
else
    echo -e "${YELLOW}⚠️  EMAIL_TO not set (needed for email alerts)${NC}"
fi

if [ -n "$EMAIL_PASSWORD" ]; then
    echo -e "${GREEN}✅ EMAIL_PASSWORD is set${NC}"
else
    echo -e "${YELLOW}⚠️  EMAIL_PASSWORD not set (needed for email alerts)${NC}"
fi

# Check dependencies
echo ""
echo "6. Python Dependencies:"
deps=("requests" "beautifulsoup4" "python-dotenv" "cloudscraper")

for dep in "${deps[@]}"; do
    if python3 -c "import ${dep//-/_}" 2>/dev/null; then
        echo -e "${GREEN}✅ $dep installed${NC}"
    else
        echo -e "${YELLOW}⚠️  $dep not installed${NC}"
    fi
done

# Test basic connectivity
echo ""
echo "7. Network Connectivity:"
if curl -s --head https://in.bookmyshow.com > /dev/null; then
    echo -e "${GREEN}✅ Can reach BookMyShow${NC}"
else
    echo -e "${RED}❌ Cannot reach BookMyShow${NC}"
fi

# Summary
echo ""
echo "========================================"
echo "📊 SUMMARY"
echo "========================================"
echo ""
echo "To complete setup:"
echo "1. Set GitHub Secrets: EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD"
echo "2. Install missing dependencies: pip install -r requirements.txt"
echo "3. Test locally: python3 test_monitors.py"
echo "4. Deploy to GitHub and trigger workflow manually"
echo ""
echo "Recommended workflow to use:"
echo "  ${GREEN}.github/workflows/ticket-monitor-simple.yml${NC} (CloudScraper - most reliable)"
echo ""
echo "Test with: ${GREEN}python3 bookmyshow_cloudscraper.py${NC}"