#!/bin/bash

# Google Scholar Citation Order - Docker Wrapper Script
# This script helps run the Google Scholar scraper in Docker

# Display usage information
function display_help {
    echo "Google Scholar Citation Order - Search Tool"
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
    echo "  -h, --help               Display this help message"
    echo ""
    echo "Example:"
    echo "  $0 -k \"machine learning\" -n 20 -o results.json"
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

# Build Docker command
DOCKER_CMD="docker run -it --rm -v $(pwd)/output:/app/output google-scholar-scraper"
DOCKER_CMD="$DOCKER_CMD --keyword \"$KEYWORD\""

# Add optional parameters
if [ ! -z "$RESULTS" ]; then
    DOCKER_CMD="$DOCKER_CMD --results $RESULTS"
fi

if [ ! -z "$YEAR_FROM" ]; then
    DOCKER_CMD="$DOCKER_CMD --year-from $YEAR_FROM"
fi

if [ ! -z "$YEAR_TO" ]; then
    DOCKER_CMD="$DOCKER_CMD --year-to $YEAR_TO"
fi

if [ ! -z "$MIN_CITATIONS" ]; then
    DOCKER_CMD="$DOCKER_CMD --min-citations $MIN_CITATIONS"
fi

if [ ! -z "$SORT_BY_DATE" ]; then
    DOCKER_CMD="$DOCKER_CMD $SORT_BY_DATE"
fi

if [ ! -z "$OUTPUT" ]; then
    DOCKER_CMD="$DOCKER_CMD --output /app/output/$OUTPUT"
fi

# Run the Docker command
echo "Running search: $KEYWORD"
eval $DOCKER_CMD

echo ""
if [ ! -z "$OUTPUT" ]; then
    echo "Results saved to output/$OUTPUT"
fi
echo "Search completed" 