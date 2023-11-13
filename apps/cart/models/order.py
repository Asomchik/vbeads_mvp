"""
Models Order and OrderItem for managing orders, products, reserving and sales.
Contains customer details.
Order is cart-based and contains OderItems,
each representing an available product with a fixed price.
"""

from django.db import models

from apps.catalog.models import Product
from apps.cart.models import Cart


class Order(models.Model):
    """An order associated with a cart and user-related information."""
    cart = models.ForeignKey(
        Cart, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # information from customer, needed for invoicing
    customer_email = models.EmailField(
        null=False, blank=False, verbose_name='Email')
    country = models.CharField(max_length=50, null=False, blank=False)
    message = models.TextField(
        max_length=300, null=True, blank=True,
        verbose_name='Message from buyer')

    # for admins notes
    memo = models.TextField(
        null=True, blank=True, verbose_name='Sellers comments')

    ORDER_STATUSES = [
        ('NEW', 'New order'),
        ('WIP', 'In progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELED', 'Canceled'),
        ('RESERVED', 'Reserved by admin'),
    ]
    status = models.CharField(
        max_length=20, default='NEW', choices=ORDER_STATUSES)

    class Meta:
        ordering = ['-created', ]

    def __str__(self):
        return f'Order №{self.pk} from {self.created.date()}'


class OrderItem(models.Model):
    """ An item in an order, fixing the price at the time of the order."""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField(default=0, blank=False)

    # is used only in OrderAdmin displaying OrderItems in line inside Order
    # '' - needed to remove unneeded line of text there
    def __str__(self):
        return ''
