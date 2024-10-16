FROM python:3.12-alpine
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
