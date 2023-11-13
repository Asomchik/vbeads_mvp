"""
This module contains a collection of utility functions
 for managing order and cart statuses and behavior.
 These functions are designed to be used both by users and administrators.
"""
from django.contrib.sessions.models import Session
from apps.cart.models import Cart


def get_or_create_cart_for_session(session_store_obj):
    """ Get or create a Cart instance associated with a session."""
    # for a saved session the key is available
    session_key = session_store_obj.session_key
    if not session_key:
        # for a new session (not stored in DB) the key is missing.
        # it becomes available after save()
        session_store_obj.save()
        session_key = session_store_obj.session_key
    session = Session.objects.get(session_key=session_key)

    # attempt to getting a Cart for current session with status 'NEW'
    cart = Cart.objects.filter(session=session, status='NEW').first()
    # if no Cart was found, create a new one
    if not cart:
        cart = Cart.objects.create(session=session, status='NEW')
    return cart


def set_reserve_for_order_items(order):
    """ Set the 'reserved' status for products in the given Order."""
    order_content = order.items.all()
    for item in order_content:
        item.product.reserved = True
        item.product.save()
    order.status = 'RESERVED'
    order.save()


def cancel_order(order):
    """ Set the 'canceled' status for the given Order
    and remove reserve from all its items"""
    order_content = order.items.all()
    for item in order_content:
        item.product.reserved = False
        item.product.save()
    order.status = 'CANCELED'
    order.save()


def progress_order(order):
    """ Mark the Order as processed by an admin and reserve all items"""
    order_content = order.items.all()
    for item in order_content:
        item.product.reserved = True
        item.product.save()
    order.status = 'WIP'
    order.save()


def sell_order(order):
    """ Set status not in_stock for products in Order"""
    order_content = order.items.all()
    for item in order_content:
        item.product.reserved = False
        item.product.in_stock = False
        item.product.save()
    order.status = 'COMPLETED'
    order.save()
