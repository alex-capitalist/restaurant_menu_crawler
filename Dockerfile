FROM python:3.11-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y \
    # Core dependencies
    wget curl ca-certificates gnupg \
    # Playwright dependencies
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 \
    libasound2 libatspi2.0-0 libxshmfence1 libwayland-client0 libwayland-egl1 \
    libwayland-server0 xdg-utils \
    # PDF processing (PyMuPDF)
    libmupdf-dev \
    # XML processing (lxml)
    libxml2-dev libxslt1-dev \
    # Fonts
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies and Playwright browsers in one layer
# This ensures they stay in sync and reduces image layers
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m playwright install --with-deps

COPY . .

# Create output directory
RUN mkdir -p /app/output

# Default environment variables for local model
ENV OPENAI_API_BASE=http://host.docker.internal:1234/v1
ENV OPENAI_API_KEY=sk-noauth
ENV OPENAI_MODEL=gpt-oss-20b

CMD ["python", "src/main.py", "--input", "input/restaurants.json", "--types", "input/menutypes.json", "--formats", "input/menuformats.json", "--out", "output/output.json"]
