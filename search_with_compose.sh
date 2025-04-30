#!/bin/bash

# Google Scholar Citation Order - Docker Compose Wrapper Script
# This script helps run the Google Scholar scraper using Docker Compose

# Display usage information
function display_help {
    echo "Google Scholar Citation Order - Docker Compose Search Tool"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -k, --keyword KEYWORD    Search keyword (required)"
    echo "  -n, --results NUMBER     Number of results (default: 10)"
    echo "  -f, --year-from YEAR     Start year for filtering"
    echo "  -t, --year-to YEAR       End year for filtering"
    echo "  -c, --min-citations NUM  Minimum citation count"
    echo "  -o, --output FILENAME    Output filename (.json or .csv)"
    echo "  -d, --sort-by-date       Sort by date (default: citation count)"
    echo "  -p, --max-pages NUM      Maximum number of pages to search"
    echo "  -h, --help               Display this help message"
    echo ""
    echo "Example:"
    echo "  $0 -k \"machine learning\" -n 20 -p 50 -o results.json"
    echo ""
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in the PATH"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p output

# Parse command line arguments
PARAMS=""
KEYWORD=""
RESULTS="10"
YEAR_FROM=""
YEAR_TO=""
MIN_CITATIONS=""
OUTPUT=""
SORT_BY_DATE=""
MAX_PAGES=""

while (( "$#" )); do
    case "$1" in
        -k|--keyword)
            KEYWORD="$2"
            shift 2
            ;;
        -n|--results)
            RESULTS="$2"
            shift 2
            ;;
        -f|--year-from)
            YEAR_FROM="$2"
            shift 2
            ;;
        -t|--year-to)
            YEAR_TO="$2"
            shift 2
            ;;
        -c|--min-citations)
            MIN_CITATIONS="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -p|--max-pages)
            MAX_PAGES="$2"
            shift 2
            ;;
        -d|--sort-by-date)
            SORT_BY_DATE="--sort-by-date"
            shift
            ;;
        -h|--help)
            display_help
            exit 0
            ;;
        -*|--*=) # unsupported flags
            echo "Error: Unsupported flag $1" >&2
            display_help
            exit 1
            ;;
        *) # preserve positional arguments
            PARAMS="$PARAMS $1"
            shift
            ;;
    esac
done

# Check if keyword is provided
if [ -z "$KEYWORD" ]; then
    echo "Error: Search keyword is required"
    display_help
    exit 1
fi

# Set default output filename if not provided
if [ -z "$OUTPUT" ]; then
    # Replace spaces with underscores in keyword for filename
    SAFE_KEYWORD=$(echo "$KEYWORD" | tr ' ' '_')
    OUTPUT="${SAFE_KEYWORD}_results.json"
fi

# Build docker-compose command
COMMAND="--keyword \"$KEYWORD\" --results $RESULTS"

if [ ! -z "$YEAR_FROM" ]; then
    COMMAND="$COMMAND --year-from $YEAR_FROM"
fi

if [ ! -z "$YEAR_TO" ]; then
    COMMAND="$COMMAND --year-to $YEAR_TO"
fi

if [ ! -z "$MIN_CITATIONS" ]; then
    COMMAND="$COMMAND --min-citations $MIN_CITATIONS"
fi

if [ ! -z "$SORT_BY_DATE" ]; then
    COMMAND="$COMMAND $SORT_BY_DATE"
fi

if [ ! -z "$MAX_PAGES" ]; then
    COMMAND="$COMMAND --max-pages $MAX_PAGES"
fi

COMMAND="$COMMAND --output /app/output/$OUTPUT"

# Update docker-compose.yml with the new command
cat > docker-compose.yml << EOF
version: '3.8'

services:
  searcher:
    build: .
    image: google-scholar-searcher
    container_name: google_scholar_searcher
    volumes:
      - ./app:/app/app
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - GOOGLE_SCHOLAR_URL=https://scholar.google.com
      - SEARCH_DELAY=2
      - MAX_PAGE_COUNT=100
      - USER_AGENT_ROTATION=true
      - HEADLESS=true
      - BROWSER_TYPE=chrome
      - LOG_LEVEL=INFO
    command: $COMMAND
EOF

# Run Docker Compose
echo "Running search: '$KEYWORD'"
echo "Results will be saved to output/$OUTPUT"
echo ""

docker compose up

echo ""
echo "Search completed"
echo "Results saved to output/$OUTPUT" 