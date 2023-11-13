from apps.cart.models import CartItem
from utils import get_or_create_cart_for_session


class CartContentMixin:
    # This mixin adds cart-related data to the context of a Django view.
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = get_or_create_cart_for_session(self.request.session)

        context['cart'] = cart
        cart_content = list(item.product for item in CartItem.objects.filter(cart=cart))
        context['cart_content'] = cart_content
        return context
