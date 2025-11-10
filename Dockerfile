# Use official Python image as base, slim for small size
FROM python:3.10-slim

# Set environment variables for python output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Launch app
CMD ["python", "swami.py"]