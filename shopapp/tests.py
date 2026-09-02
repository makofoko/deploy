import json
from django.test import TestCase
from django.urls import reverse
from shopapp.models import Order, Product
from django.contrib.auth.models import User, Permission


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаём пользователя
        cls.user = User.objects.create_user(username="testuser", password="password")
        # даём право на просмотр заказа
        permission = Permission.objects.get(codename="view_order")
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.login(username="testuser", password="password")
        self.order = Order.objects.create(
            delivery_address="Test Street 123",
            promocode="PROMO10",
            user=self.user,
        )

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        url = reverse("shopapp:order_detail", kwargs={"pk": self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        # проверка контекста
        self.assertEqual(response.context["order"].pk, self.order.pk)


class OrdersExportFixtureTest(TestCase):
    fixtures = ["users.json", "products.json", "orders.json"]

    def setUp(self):
        # Берём пользователя из фикстуры и логинимся
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

    def test_export_with_fixtures(self):
        url = reverse("shopapp:orders_export")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # ORM-запрос
        orders = Order.objects.select_related("user").prefetch_related("products").all()
        expected = []
        for order in orders:
            expected.append({
                "id": order.id,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.id,
                "products": list(order.products.values_list("id", flat=True)),
            })

        # сравнение целиком
        self.assertEqual(data["orders"], expected)