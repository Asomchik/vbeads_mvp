from django import forms

from apps.cart.models import Cart, CartItem, Order


class OrderForm(forms.ModelForm):
    agree_with_policies = forms.BooleanField(required=True)
    class Meta:
        model = Order
        fields = ['customer_email', 'country', 'message']
