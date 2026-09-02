from django.core.management.base import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    """Создает тестовые продукты."""

    def handle(self, *args, **options):
        self.stdout.write("Creating products...")
        product_names = ["Ноутбук", "Смартфон", "Монитор"]

        for name in product_names:
            product, created = Product.objects.get_or_create(name=name, price=1000)
            if created:
                self.stdout.write(f"Created product: {product.name}")

        self.stdout.write(self.style.SUCCESS("Products created successfully"))