"""
Custom template tag for dynamically construct header menu of categories
"""
from django import template

from apps.catalog.models import Category

register = template.Library()


@register.simple_tag()
def get_categories_for_header():
    """ getting categories specially marked for showing in header menu"""
    return Category.objects.filter(
            parent=None, products__isnull=False,
            visibility=True, show_at_header=True,
        ).distinct().order_by('view_priority')
