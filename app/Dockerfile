# Use the official lightweight Python 3.11 image
FROM python:3.11-slim

# Set environment variables:
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk
# PYTHONUNBUFFERED: Ensures immediate flushing of logs to stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy dependency specifications and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and web templates
COPY app.py .
COPY templates ./templates

# Expose port 5000 for the Flask application
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]
