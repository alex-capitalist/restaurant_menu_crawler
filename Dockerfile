FROM python:3.11-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for Playwright and PDFs
RUN apt-get update && apt-get install -y \
    wget curl ca-certificates fonts-dejavu libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libasound2 libatspi2.0-0 libxshmfence1 libwayland-client0 \
    libwayland-egl1 libwayland-server0 xdg-utils gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install browsers
RUN python -m playwright install --with-deps

COPY . .

CMD ["python", "src/main.py", "--input", "restaurants.json", "--types", "menutypes.json", "--formats", "menuformat.json", "--out", "output.json"]
