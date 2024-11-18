# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y wget gnupg2 unzip curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y \
    google-chrome-stable \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install specific version of ChromeDriver
RUN wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/119.0.6045.105/chromedriver_linux64.zip" \
    && cd /tmp \
    && unzip chromedriver.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -f /tmp/chromedriver.zip

# Install specific version of Chrome
RUN apt-get update && apt-get install -y \
    google-chrome-stable=119.0.6045.105-1 \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome paths
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Create and set working directory
WORKDIR /app

# Copy requirements first for better cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Verify Chrome and ChromeDriver installation
RUN google-chrome --version && chromedriver --version

# Expose port
EXPOSE 5000

# Start command with health check
CMD gunicorn --preload api:app --bind 0.0.0.0:${PORT:-5000} --timeout 180 --workers 1
