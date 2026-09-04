from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductArchiveView,
    OrderListView, OrderDetailView, OrderCreateView, OrderUpdateView, OrderDeleteView,
    OrdersExportView, LatestProductsFeed,
    UserOrdersListView, UserOrdersExportView,  # новые классы
)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from .views import (
    ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductArchiveView,
    OrderListView, OrderDetailView, OrderCreateView, OrderUpdateView, OrderDeleteView,
    OrdersExportView, LatestProductsFeed,
    UserOrdersListView, UserOrdersExportView,
)
from .api import ProductViewSet, OrderViewSet


app_name = 'shopapp'

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),  # добавляем админку
    path('', include(router.urls)),   # API через DRF

    # продукты
    path('products/', ProductListView.as_view(), name='products_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/archive/', ProductArchiveView.as_view(), name='product_archive'),
    path("products/latest/feed/", LatestProductsFeed(), name="latest_products_feed"),

    # заказы
    path('orders/', OrderListView.as_view(), name='orders_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/edit/', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    path('orders/export/', OrdersExportView.as_view(), name='orders_export'),

    # новые маршруты для кеширования
    path("users/<int:user_id>/orders/", UserOrdersListView.as_view(), name="user_orders"),
    path("users/<int:user_id>/orders/export/", UserOrdersExportView.as_view(), name="user_orders_export"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
