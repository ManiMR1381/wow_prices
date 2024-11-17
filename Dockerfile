FROM mcr.microsoft.com/playwright/python:v1.39.0-focal

WORKDIR /app

# Copy requirements first for better cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Install only Chromium browser
RUN python -m playwright install chromium

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV GUNICORN_CMD_ARGS="--timeout 120 --workers 2 --threads 4 --worker-class gthread"

# Command to run the application
CMD gunicorn api:app --bind 0.0.0.0:$PORT
