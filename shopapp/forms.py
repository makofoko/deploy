from django import forms
from .models import Product, Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "discount", "archived"]

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["delivery_address", "promocode", "user", "products"]

class OrderImportForm(forms.Form):
    file = forms.FileField()