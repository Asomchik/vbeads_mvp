"""
Provides functionality for render cart page.
"""
from django.views.generic import TemplateView

from apps.cart.models import CartItem
from apps.cart.forms import OrderForm
from utils import get_or_create_cart_for_session


class CartView(TemplateView):
    """View class for displaying the cart page."""
    template_name = 'cart.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """Retrieves the context data to be used in rendering the cart page."""
        context = super().get_context_data(**kwargs)
        context['head_tag_title'] = f'Olga Vilnova Lampwork Beads'

        context['form'] = OrderForm()

        cart = get_or_create_cart_for_session(self.request.session)
        cart_content = (
            CartItem.objects.filter(cart=cart)
            .select_related('product')
        )
        context['cart'] = cart
        context['cart_content'] = cart_content

        # Organize the cart items into categories within the context:
        # depending on products availability
        context['items_in_stock'] = [
            item for item in cart_content
            if item.product.in_stock and not item.product.reserved
        ]

        context['subtotal'] = sum([
            item.product.price for item in cart_content
            if item.product.in_stock and not item.product.reserved
        ])

        context['items_on_hold'] = [
            item for item in cart_content
            if item.product.in_stock and item.product.reserved
        ]
        context['items_sold'] = [
            item for item in cart_content
            if not item.product.in_stock
        ]
        return context
