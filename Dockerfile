FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install NLTK data
RUN python -m nltk.downloader punkt punkt_tab

COPY news_agent.py .

# Run the application
CMD ["python", "news_agent.py", "serve"]
