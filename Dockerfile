FROM python:3.11
WORKDIR /app

# Install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

EXPOSE 8000

# Run the application
ENTRYPOINT ["python", "/app/main.py"]
