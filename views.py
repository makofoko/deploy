import logging
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.core.cache import cache
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Product, Order
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ProductSerializer, OrderSerializer
from django.contrib.syndication.views import Feed

log = logging.getLogger(__name__)

# --- HTML Views для продуктов ---
class ProductListView(ListView):
    model = Product
    template_name = "shopapp/products-list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(archived=False)

class ProductDetailView(DetailView):
    model = Product
    template_name = "shopapp/product-detail.html"
    context_object_name = "product"

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    fields = ["name", "description", "price", "discount"]
    template_name = "shopapp/product-form.html"
    success_url = reverse_lazy("shopapp:products_list")

    def test_func(self):
        return self.request.user.has_perm("shopapp.add_product")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ["name", "description", "price", "discount"]
    template_name = "shopapp/product-form.html"
    success_url = reverse_lazy("shopapp:products_list")

    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_superuser or (
            self.request.user == obj.created_by and
            self.request.user.has_perm("shopapp.change_product")
        )

class ProductArchiveView(DeleteView):
    model = Product
    template_name = "shopapp/product-confirm-archive.html"
    success_url = reverse_lazy("shopapp:products_list")

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        product.archived = True
        product.save()
        return redirect(self.success_url)

# --- HTML Views для заказов ---
class OrderListView(ListView):
    model = Order
    template_name = "shopapp/orders-list.html"
    context_object_name = "orders"

class OrderDetailView(DetailView):
    model = Order
    template_name = "shopapp/order-detail.html"
    context_object_name = "order"

class OrderCreateView(CreateView):
    model = Order
    fields = ["delivery_address", "promocode", "user", "products"]
    template_name = "shopapp/order-form.html"
    success_url = reverse_lazy("shopapp:orders_list")

class OrderUpdateView(UpdateView):
    model = Order
    fields = ["delivery_address", "promocode", "user", "products"]
    template_name = "shopapp/order-form.html"
    success_url = reverse_lazy("shopapp:orders_list")

class OrderDeleteView(DeleteView):
    model = Order
    template_name = "shopapp/order-confirm-delete.html"
    success_url = reverse_lazy("shopapp:orders_list")

# --- Экспорт всех заказов (для staff) ---
class OrdersExportView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        orders = Order.objects.select_related("user").prefetch_related("products").all()
        serializer = OrderSerializer(orders, many=True)
        return JsonResponse({"orders": serializer.data})

# --- API ViewSet для продуктов ---
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(archived=False)
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "name"]
    ordering = ["name"]

# --- API ViewSet для заказов ---
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["user", "promocode"]
    ordering_fields = ["created_at", "delivery_address"]
    ordering = ["-created_at"]

# --- RSS Feed для последних продуктов ---
class LatestProductsFeed(Feed):
    title = "Последние товары"
    link = "/products/latest/feed/"
    description = "Новые товары в магазине"

    def items(self):
        return Product.objects.order_by("-created_at")[:10]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return f"Описание: {item.description}"

    def item_link(self, item):
        return reverse("shopapp:product_detail", args=[item.pk])

# --- Страница заказов пользователя ---
class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "shopapp/user_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        self.owner = get_object_or_404(User, pk=self.kwargs["user_id"])
        return Order.objects.filter(user=self.owner).order_by("pk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        return context

# --- Экспорт заказов пользователя с кешированием ---
class UserOrdersExportView(View):
    def get(self, request, user_id):
        cache_key = f"user_orders_{user_id}"
        data = cache.get(cache_key)
        if not data:
            owner = get_object_or_404(User, pk=user_id)
            orders = Order.objects.filter(user=owner).order_by("pk")
            serializer = OrderSerializer(orders, many=True)
            data = serializer.data
            cache.set(cache_key, data, timeout=300)  # кеш на 5 минут
        return JsonResponse({"orders": data})
