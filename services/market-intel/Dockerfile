FROM python:3.9.6

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

# --workers can be scaled with CPU cores; this service is I/O-bound
# (mostly waiting on NGX/NewsAPI/Groq), so 2-4 workers per core is reasonable.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]