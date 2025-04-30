FROM python:3.11-slim

WORKDIR /app

# Install Chromium and dependencies for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libglib2.0-0 \
    libnss3 \
    libgbm1 \
    libasound2 \
    fonts-liberation \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chromium and ChromeDriver
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Set environment variables to skip database dependencies
ENV DATABASE_URL=sqlite:///./dummy.db

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output and log directories
RUN mkdir -p logs
RUN mkdir -p output

# Default environment variables for search parameters
ENV SEARCH_DELAY=2
ENV MAX_PAGE_COUNT=100
ENV USER_AGENT_ROTATION=true
ENV HEADLESS=true
ENV BROWSER_TYPE=chrome
ENV LOG_LEVEL=INFO

# Default command (can be overridden by docker-compose)
ENTRYPOINT ["python", "run_search.py"]
CMD ["--help"] 