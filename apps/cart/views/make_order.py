"""
Provides functionality for user-initiated creation of order from cart page.
"""
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.shortcuts import HttpResponseRedirect
from django.template.loader import render_to_string

from apps.cart.models import CartItem, Order, OrderItem
from apps.cart.forms import OrderForm
from utils import get_or_create_cart_for_session, set_reserve_for_order_items


def send_confirm_to_user(order):
    """Define the way to inform user about new order creation"""
    order_products = OrderItem.objects.filter(order=order).values_list('product__title', 'price')
    products_render_dict = [{'title': prod[0], 'price':prod[1]} for prod in order_products]
    total_amount = sum(prod['price'] for prod in products_render_dict)
    # Render the email template with the order details
    context = {
        'customer_email': order.customer_email,
        'products': products_render_dict,
        'total_amount': total_amount,
    }
    email_html_content = render_to_string('email/order_created.html', context)
    # Create and send the email message
    letter = EmailMessage(
        subject='Your Order Details',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.customer_email],
        body=email_html_content,
    )
    letter.content_subtype = 'html'
    letter.send()


def send_confirm_to_admin(order):
    """Define the way to inform admin about new order creation"""
    email_content = f'new order {order.id}'
    # Create the email message
    letter = EmailMessage(
        subject='ADMIN: New order',
        body=email_content,
        from_email=settings.DEFAULT_FROM_EMAIL,

        # change to real email
        to=['admin_email@gmail.com'],
    )
    letter.send()


def make_order_from_cart(request):
    """Create Order instance (with OrderItem-s) based on Cart
    initiated by user clicking 'make order' button at Cart/WishList page"""
    if request.method != 'POST':
        return HttpResponseRedirect('main-page')
    try:
        cart = get_or_create_cart_for_session(request.session)
        form = OrderForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Error occurred, try again later.')
            return HttpResponseRedirect('main-page')
    except ObjectDoesNotExist:
        messages.error(request, 'Error occurred, try again later.')
        return HttpResponseRedirect('main-page')

    # take only non-reserved and in-stock products from cart to order
    items_in_cart = [
        item for item in CartItem.objects.filter(cart=cart)
        if item.product.in_stock and not item.product.reserved
    ]
    # create order for 'new' and non-empty cart only
    if cart.status != 'NEW' or not items_in_cart:
        messages.error(request, 'No items to be sold!')
        return HttpResponseRedirect('main-page')

    # create order
    order = Order(
        cart=cart,
        customer_email=form.cleaned_data.get('customer_email').lower(),
        country=form.cleaned_data.get('country').capitalize(),
        message=form.cleaned_data.get('message'),
        status='CREATED',
    )
    order.save()

    # fill order with items from cart
    for cart_item in items_in_cart:
        order_item = OrderItem(
            order=order,
            product=cart_item.product,
            price=cart_item.product.price,
        )
        order_item.save()

    # reserve items in order not to sell them twice
    set_reserve_for_order_items(order)

    # change cart status
    cart.status = 'ORDER'
    cart.save()

    send_confirm_to_user(order)
    send_confirm_to_admin(order)

    messages.success(request, 'Order created. E-mail with details was sent.'
                              ' Please, wait for invoice')
    return_path = request.POST.get('return_path', '/')
    return HttpResponseRedirect(return_path)
