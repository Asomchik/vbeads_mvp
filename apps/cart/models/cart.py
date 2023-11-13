"""
Models Cart and CartItem for managing shopping carts and sales.
Cart is associated with a session instance and contains CartItems,
each representing a product with a fixed price.
"""


from django.contrib.sessions.models import Session
from django.db import models

from apps.catalog.models import Product


class Cart(models.Model):
    """A cart of products connected to a user by Session"""
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    CART_STATUSES = [
        ('NEW', 'New cart'),
        ('OLD', 'Old cart'),
        ('ORDER', 'Order made'),
    ]
    status = models.CharField(
        max_length=5, default='NEW', choices=CART_STATUSES)


class CartItem(models.Model):
    """A product within a cart with a fixed price."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField(default=0, blank=False)
