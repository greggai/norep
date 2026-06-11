#!/bin/bash
# Fetch GitHub security alerts via gh CLI
# Usage: ./fetch.sh <repo_url_or_owner/repo>
# Output: JSON to stdout

set -e

# Check gh CLI is available and authenticated
if ! command -v gh &> /dev/null; then
    echo "ERROR: gh CLI is not installed. Install from: https://cli.github.com/" >&2
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "ERROR: gh CLI is not authenticated. Run 'gh auth login'" >&2
    exit 1
fi

# Parse repo from input
INPUT="${1:-}"
if [[ -z "$INPUT" ]]; then
    echo "Usage: ./fetch.sh <repo_url_or_owner/repo>" >&2
    exit 1
fi

# Extract owner/repo from URL or direct input
if [[ "$INPUT" =~ github\.com/([^/]+)/([^/]+) ]]; then
    REPO="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
elif [[ "$INPUT" =~ ^[^/]+/[^/]+$ ]]; then
    REPO="$INPUT"
else
    echo "ERROR: Could not parse repository from: $INPUT" >&2
    exit 1
fi

echo "Fetching security alerts for: $REPO" >&2

# Fetch each alert type, capturing errors gracefully
fetch_alerts() {
    local endpoint="$1"
    local result
    if result=$(gh api "$endpoint" 2>&1); then
        echo "$result"
    else
        echo "[]"
    fi
}

# Build JSON output
CODE_SCANNING=$(fetch_alerts "/repos/$REPO/code-scanning/alerts?state=open&per_page=100")
DEPENDABOT=$(fetch_alerts "/repos/$REPO/dependabot/alerts?state=open&per_page=100")
SECRET_SCANNING=$(fetch_alerts "/repos/$REPO/secret-scanning/alerts?state=open&per_page=100")

# Output combined JSON using jq
jq -n \
    --arg repo "$REPO" \
    --argjson code_scanning "$CODE_SCANNING" \
    --argjson dependabot "$DEPENDABOT" \
    --argjson secret_scanning "$SECRET_SCANNING" \
    '{
        repository: $repo,
        code_scanning: $code_scanning,
        dependabot: $dependabot,
        secret_scanning: $secret_scanning
    }'
