"""
URL configuration (global). No additional URL in apps directories
"""
import os
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.urls import path

from apps.catalog.views import CategoryView, ProductView
from apps.cart.views import (
    CartView,
    add_item, remove_item,
    make_order_from_cart,
)

urlpatterns = [
    # custom admin panel URL
    path('admin/', admin.site.urls),
    # general views
    path('', CategoryView.as_view(is_main_page=True), name='main-page'),
    path('catalog/<str:slug>/', CategoryView.as_view(), name='category'),
    path('product/<str:slug>/', ProductView.as_view(), name='product'),
    path('cart/', CartView.as_view(), name='cart'),
    # static pages
    path('about/',
         TemplateView.as_view(template_name='static_pages/about.html'),
         name='about'),
    path('faq/',
         TemplateView.as_view(template_name='static_pages/faq.html'),
         name='faq'),
    path('policies/',
         TemplateView.as_view(template_name='static_pages/policies.html'),
         name='policies'),

    # non-public (API-like) for internal use URLs
    path('remove_item/', remove_item, name='remove-item'),
    path('add_item/', add_item, name='add-item'),
    path('make_order/', make_order_from_cart, name='make-order-from-cart'),

]

if settings.DEBUG and (
        os.path.exists(os.path.join(settings.BASE_DIR, 'local_settings.py'))):
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
