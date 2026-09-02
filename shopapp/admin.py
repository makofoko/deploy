from django.contrib import admin
from .models import Product, Order
import csv
from django.shortcuts import render, redirect
from django.urls import path
from .forms import OrderImportForm

class OrderInline(admin.TabularInline):
    model = Order.products.through
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "price", "discount", "archived")
    search_fields = ("name", "price")
    inlines = [OrderInline]

    fieldsets = (
        (None, {"fields": ("name", "description")}),
        ("Цена", {"fields": ("price", "discount")}),
        ("Дополнительно", {"fields": ("archived",), "classes": ("collapse",)}),
    )

    actions = ["make_archived"]

    def make_archived(self, request, queryset):
        updated = queryset.update(archived=True)
        self.message_user(request, f"{updated} продуктов архивировано.")
    make_archived.short_description = "Архивировать выбранные продукты"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "promocode", "created_at")
    search_fields = ("promocode", "user__username")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
    change_list_template = "shopapp/orders_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-orders/", self.import_csv, name="shopapp_order_import"),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = OrderImportForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data["file"]
                reader = csv.DictReader(file.read().decode("utf-8").splitlines())
                for row in reader:
                    order = Order.objects.create(
                        delivery_address=row["delivery_address"],
                        promocode=row["promocode"],
                        user_id=row["user_id"],
                    )
                    product_ids = row["products"].split(",")
                    order.products.set(Product.objects.filter(id__in=product_ids))
                return redirect("..")
        else:
            form = OrderImportForm()
        return render(request, "admin/csv_form.html", {"form": form})
