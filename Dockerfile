FROM python:3.11-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pip install --upgrade pip && pip install pipenv && pipenv install --system --skip-lock

COPY . .

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
