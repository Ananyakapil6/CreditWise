# Use official Python 3.10 image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=10000

# Set work directory
WORKDIR /app

# Copy requirements first to leverage caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port Flask will run on
EXPOSE 10000

# Command to run the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
