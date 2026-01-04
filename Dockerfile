FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Python dependencies including required packages for ORM
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy asyncpg psycopg2-binary pydantic[email]

# Copy application code
COPY main.py .

# Copy src directory
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f --max-time 3 http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
