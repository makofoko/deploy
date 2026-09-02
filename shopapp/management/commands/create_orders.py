from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Order, Product


class Command(BaseCommand):
    """Создает тестовый заказ и привязывает продукты."""

    def handle(self, *args, **options):
        self.stdout.write("Creating order...")
        user = User.objects.first()
        if not user:
            self.stdout.write("No users found. Please run createsuperuser.")
            return

        # Получаем или создаем заказ
        order, created = Order.objects.get_or_create(
            delivery_address="ул. Пушкина, дом 10",
            promocode="SALE20",
            user=user,
        )

        if created:
            # Привязываем все существующие продукты к этому заказу
            products = Product.objects.all()
            for product in products:
                order.products.add(product)
            order.save()
            self.stdout.write(f"Created order #{order.id} for user {user.username}")

        self.stdout.write(self.style.SUCCESS("Order created successfully"))