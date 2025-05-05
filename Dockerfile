FROM mcr.microsoft.com/playwright/python:v1.51.0-noble

# Set working directory
WORKDIR /app

# Copy your project files into the container
COPY . .

# Install Python requirements (including playwright)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install

# Run your script
CMD ["python3", "visier_object_inheritance_tracing.py"]

