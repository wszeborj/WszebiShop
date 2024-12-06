FROM python:3.10-alpine
WORKDIR /app
ENV PYTHONUNBUFFERED=1
RUN pip install poetry==1.8.4
COPY poetry.lock pyproject.toml ./
RUN poetry check
RUN poetry install --no-interaction --no-cache --without dev
COPY . .
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
