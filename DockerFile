# Use an official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy project files to the container
COPY . .

# Install dependencies if you have any
# If you use a requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || true

# Expose the port (match with your PORT env var)
EXPOSE 12345

# Run the server
CMD ["python", "server.py"]
