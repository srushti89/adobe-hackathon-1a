# Use a lightweight Python image for amd64 architecture
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy everything into container
COPY . /app

# Install only the necessary dependency
RUN pip install --no-cache-dir pymupdf

# Make sure input/output folders exist
RUN mkdir -p /app/input /app/output

# Set script to run when container starts
ENTRYPOINT ["python", "process_pdfs.py"]
