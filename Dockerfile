# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port for Cloud Run
ENV PORT 8080
EXPOSE 8080

# Run the application
#CMD ["python", "main.py"]
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app --log-level info