# Use an official lightweight Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install python dependencies (wheels contain pre-compiled binaries)
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files into the docker image
COPY . /app/

# Create writable runtime storage directories
RUN mkdir -p /app/uploads \
    && mkdir -p /app/static/uploads \
    && mkdir -p /app/static/generated_tickets \
    && chmod -R 775 /app/uploads /app/static/uploads /app/static/generated_tickets

# Expose the port Gunicorn binds to
EXPOSE 8000

# Start Gunicorn WSGI server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
