# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV CHROME_BIN=/opt/chrome-linux64/chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    curl \
    xvfb \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libx11-xcb1 \
    # GTK and ATK dependencies
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libpango-1.0-0 \
    libcairo2 \
    # Additional dependencies
    libdbus-1-3 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Testing and ChromeDriver
RUN wget -O chrome-linux.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chrome-linux64.zip" \
    && wget -O chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip" \
    && unzip chrome-linux.zip -d /opt/ \
    && unzip chromedriver.zip -d /opt/ \
    && mv /opt/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && chmod +x /opt/chrome-linux64/chrome \
    && rm -f chrome-linux.zip chromedriver.zip

# Create and set working directory
WORKDIR /app

# Copy requirements first for better cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a script to start Xvfb and the application
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1280x1024x24 &\nsleep 1\nexec "$@"' > /usr/local/bin/start.sh \
    && chmod +x /usr/local/bin/start.sh

# Start command with health check
ENTRYPOINT ["/usr/local/bin/start.sh"]
CMD ["gunicorn", "--preload", "api:app", "--bind", "0.0.0.0:${PORT:-5000}", "--timeout", "180", "--workers", "1"]
