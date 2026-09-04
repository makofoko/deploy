import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapp.settings')  # замени core на имя своей папки
application = get_wsgi_application()

