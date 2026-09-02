# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY . /app/

# Create runtime directories
RUN mkdir -p /app/uploads \
    /app/static/uploads/event_posters \
    /app/static/uploads/user_documents \
    /app/static/generated_tickets \
    /app/instance

# Expose Gunicorn port
EXPOSE 8000

# Start Gunicorn WSGI server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
