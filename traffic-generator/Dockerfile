# Lightweight Python image for traffic generator
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy traffic generator script (uses Python standard library urllib, no external packages needed)
COPY generator.py .

CMD ["python", "generator.py"]
