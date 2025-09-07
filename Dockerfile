FROM python:3.11-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install essential system dependencies first
RUN apt-get update && apt-get install -y \
    # Core utilities
    wget curl ca-certificates gnupg \
    # Essential libraries for Python packages
    libxml2-dev libxslt1-dev \
    libmupdf-dev \
    # Playwright system dependencies (as suggested by Playwright)
    libatk-bridge2.0-0 libpango-1.0-0 libcairo2 \
    # Additional GUI libraries
    libnss3 libatk1.0-0 libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 libatspi2.0-0 libxshmfence1 \
    # Fonts
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install chromium

COPY . .

# Create output directory
RUN mkdir -p /app/output

# Default environment variables for local model
ENV OPENAI_API_BASE=http://host.docker.internal:1234/v1
ENV OPENAI_API_KEY=sk-noauth
ENV OPENAI_MODEL=gpt-oss-20b

# Set Python path to include src directory
ENV PYTHONPATH=/app/src

CMD ["python", "-m", "src.main", "--input", "input/restaurants.json", "--types", "input/menutypes.json", "--formats", "input/menuformats.json", "--out", "output/output.json"]
