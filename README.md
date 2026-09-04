# Deploying Django Project

Учебный проект для практической работы по деплою Django‑приложения с использованием Docker, Pipenv и SSH.

## 📂 Структура проекта

Deploying/
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── Pipfile
├── Pipfile.lock
├── deploy/              # Папка проекта (настройки)
│   ├── init.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── shopapp/             # Приложение
│   ├── init.py
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   └── migrations/
└── templates/           # Шаблоны
└── admin/