# Base Stage
FROM python:3.11-slim-buster as base

WORKDIR /app

# Install dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Production Stage
FROM base as production

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api.solomon.main:app", "--host", "0.0.0.0", "--port", "8000"]
