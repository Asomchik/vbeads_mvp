"""
Provides functionality for adding and removing items to cart.
"""
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import HttpResponseRedirect
# from apps.cart.models import Cart, CartItem
from apps.cart.models import CartItem

from apps.catalog.models import Product

from utils import get_or_create_cart_for_session


def add_item(request):
    """
    Adding item to cart by POST request.
    Create new cart for session if necessary.
    """
    try:
        cart = get_or_create_cart_for_session(request.session)
        product_pk = request.POST.get('product_pk')
        product = Product.objects.get(pk=product_pk)
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/')

    if not CartItem.objects.filter(cart=cart, product=product):
        cart_item = CartItem(
            cart=cart,
            product=product,
            price=product.price,
            )
        cart_item.save()

    return_path = request.POST.get('return_path', '/')
    return HttpResponseRedirect(return_path)


def remove_item(request):
    """
    Removing item from cart by POST request.
    No affect cart without item
    """
    try:
        cart = get_or_create_cart_for_session(request.session)
        product_pk = request.POST.get('product_pk')
        product = Product.objects.get(pk=product_pk)
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/')

    if product_in_cart := CartItem.objects.filter(cart=cart, product=product):
        product_in_cart.delete()

    return_path = request.POST.get('return_path', '/')
    return HttpResponseRedirect(return_path)
