#!/usr/bin/env bash
# OpenEnv Submission Validator

set -uo pipefail

# 1. Colors & Formatting Setup
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BOLD='' NC=''
fi

# 2. Check for URL argument
if [ $# -eq 0 ]; then
    echo -e "${RED}${BOLD}Error: No Space URL provided.${NC}"
    echo "Usage: bash validate-submission.sh <huggingface_url>"
    exit 1
fi

SPACE_URL=$1

echo -e "${YELLOW}${BOLD}Starting Phase 1 Validation...${NC}"
echo "Target: $SPACE_URL"
echo "------------------------------------------------"

# [Check 1/3] Reachability
echo -n "[1/3] Checking if Space is live... "
# Use curl to check if the page returns a 200 OK status
if curl -s --head "$SPACE_URL" | grep -E "200|301|302" > /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo -e "      ${YELLOW}Advice: Check if your Space is set to 'Public'.${NC}"
    exit 1
fi

# [Check 2/3] Mandatory Local Files
echo -n "[2/3] Checking for mandatory root files... "
MISSING_FILES=()
[[ ! -f "openenv.yaml" ]] && MISSING_FILES+=("openenv.yaml")
[[ ! -f "inference.py" ]] && MISSING_FILES+=("inference.py")
[[ ! -f "pyproject.toml" ]] && MISSING_FILES+=("pyproject.toml")

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo -e "      ${YELLOW}Missing: ${MISSING_FILES[*]}${NC}"
    exit 1
fi

# [Check 3/3] OpenEnv Structure Validation
echo -n "[3/3] Running OpenEnv structure check... "
# Check if openenv-core is installed to run the official validator
if command -v openenv &> /dev/null; then
    # Runs the actual openenv internal validation logic
    if openenv validate --path . > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAILED (Check your openenv.yaml syntax)${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}SKIPPED (openenv-core not found locally)${NC}"
    echo "      Note: Local structure looks correct, but install 'pip install openenv-core' for a full check."
fi

echo "------------------------------------------------"
echo -e "${GREEN}${BOLD}SUCCESS: All Phase 1 checks passed!${NC}"
echo -e "You are ready to submit your ZIP and URL to the portal."