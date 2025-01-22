FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster Python package installation
RUN pip install uv

# Create a virtual environment using uv
RUN uv venv

# Activate the virtual environment in subsequent RUN commands
SHELL ["/bin/bash", "-c"]
RUN source .venv/bin/activate

# Copy dependency files
COPY pyproject.toml .

# Install dependencies using uv (now within the venv)
RUN uv pip install -e .
RUN uv add uvicorn

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uv", "run", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
