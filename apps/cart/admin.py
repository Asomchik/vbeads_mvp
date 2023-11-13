"""
Admin pages for Cart and Order
"""
from django import forms
from django.contrib import admin
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from easy_thumbnails.templatetags.thumbnail import thumbnail_url

from apps.cart.models import Cart, CartItem, Order, OrderItem

from utils import (
    set_reserve_for_order_items,
    cancel_order, progress_order, sell_order,
)


class OrderItemsInline(admin.TabularInline):
    """ Show all connected products on the change Order instance page"""
    model = OrderItem
    extra = 0
    fields = ('get_image', 'product', 'price')
    readonly_fields = ('get_image',)

    def get_image(self, obj):
        """ show image for OrderItem"""
        url_small = thumbnail_url(obj.product.picture_1, 'small')
        return mark_safe(f'<img src={url_small} alt="small-img">')
    get_image.short_description = 'Image'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """ Custom Order list and form for admin pages"""

    # add buttons for custom actions on the change Order instance page
    change_form_template = 'for_admin/edit_order.html'
    save_on_top = True

    # list appearance
    list_display = ('id', 'status', 'calculate_total', 'created',
                    'country', 'message', 'updated')
    list_filter = ('status', 'country')
    # list_editable = ('status',)
    actions = [
        'reserve_orders_from_list', 'un_reserve_orders_from_list',
        'complete_orders_from_list', 'cancel_orders_from_list',
    ]
    list_per_page = 100

    # instance appearance
    fields = (
        ('status', 'calculate_total'),
        ('country', 'customer_email'),
        ('message', 'memo'),
        ('created', 'updated'),
    )
    readonly_fields = ('status', 'created', 'updated', 'calculate_total')
    inlines = [OrderItemsInline]

    def formfield_for_dbfield(self, db_field, **kwargs):
        # Appearance for textarea fields
        if db_field.name in ['message', 'memo']:
            kwargs['widget'] = forms.Textarea(attrs={'rows': 4, 'cols': 40})
        # elif db_field.name == 'country':
        #     kwargs['widget'] = forms.TextInput(attrs={'size': 20})
        return super().formfield_for_dbfield(db_field, **kwargs)

    def calculate_total(self, order):
        """ Calculate subtotal for order """
        total = order.items.aggregate(Sum('price'))
        return total.get('price__sum', 0)
    calculate_total.short_description = 'Total'

    # hide unneeded buttons
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url,
                                   extra_context=extra_context)

    # define behavior for additional buttons in change Order form
    def response_change(self, request, obj):
        if "_cancel" in request.POST:
            cancel_order(obj)
        elif "_in_progress" in request.POST:
            progress_order(obj)
        elif "_complete" in request.POST:
            sell_order(obj)
        elif "_reserve" in request.POST:
            set_reserve_for_order_items(obj)
        else:
            return super().response_change(request, obj)
        return HttpResponseRedirect(".")  # stay on the same detail page

    # custom actions for Order list
    def cancel_orders_from_list(self, request, queryset):
        """ Change status to 'CANCELED' for Orders. Remove reserves."""
        for order in queryset:
            cancel_order(order)
        self.message_user(
            request, 'Status set to "Canceled". Items unreserved.')
    cancel_orders_from_list.short_description = 'Cancel orders'

    def complete_orders_from_list(self, request, queryset):
        """ Change status to 'COMPLETED' for Orders. Remove items from stock"""
        for order in queryset:
            sell_order(order)
        self.message_user(
            request, 'Status set to "Complete". Items removed from stock.')
    complete_orders_from_list.short_description = 'Complete orders'

    def reserve_orders_from_list(self, request, queryset):
        """ Change status to 'RESERVED' for Order and all its Items"""
        for order in queryset:
            set_reserve_for_order_items(order)
        self.message_user(request, 'Reserved')
    reserve_orders_from_list.short_description = 'Reserve orders'


class CartItemsInline(admin.TabularInline):
    """ Show all connected products on the change Cart instance page"""
    model = CartItem
    extra = 0
    list_display = ('get_image', 'product', )
    readonly_fields = ('get_image', 'product', 'price')

    def get_image(self, obj):
        """ Show image for OrderItem"""
        url_small = thumbnail_url(obj.product.picture_1, 'small')
        return mark_safe(f'<img src={url_small} alt="small-img">')
    get_image.short_description = 'Image'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """ Cart list and for admin pages"""
    list_display = ['id', 'view_creation_date', 'status']
    inlines = [CartItemsInline]

    def view_creation_date(self, obj):
        """ Show human-readable date at list page"""
        return obj.date_created.strftime('%Y-%m-%d')
    view_creation_date.short_description = 'Created'
