FROM python:3.11
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system --deploy
COPY . .
CMD ["gunicorn", "shopapp.wsgi:application", "--bind", "0.0.0.0:8000"]
