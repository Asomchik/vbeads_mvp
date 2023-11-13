"""
Provides functionality for render list of products page.
"""
import random
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from apps.catalog.models import Product, Category
from mixins import CartContentMixin


class CategoryView(CartContentMixin, ListView):
    """View class for displaying list or products."""
    is_main_page = False

    def get_template_names(self):
        # Use special template for 'tutorials' category
        if self.kwargs.get('slug') == 'tutorials':
            return ['tutorial_list.html']
        return ['product_list.html']

    def get_queryset(self):
        # for main page: all products in_stock and visible_after_sale
        # except 'tutorials'
        queryset = (Product.objects
                    .exclude(category__slug='tutorials')
                    .filter(Q(in_stock=True) | Q(show_after_sale=True))
                    )
        # for non-main page make queryset depending on category
        if not self.is_main_page and (slug := self.kwargs['slug']):
            # 'sale' is virtual category - filtering products by discount
            if slug == 'sale':
                queryset = (Product.objects
                            .filter(discount__gt=0, in_stock=True)
                            .order_by('-discount')
                            )
            # 'tutorials' excluded from main queryset, so new search needed
            elif slug == 'tutorials':
                queryset = Product.objects.filter(category__slug='tutorials')
            # for any other category simply adding filter by category
            else:
                category = get_object_or_404(Category, slug=slug)
                queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        # Add context variables
        context = super().get_context_data(**kwargs)
        # navigation menu - top level categories
        # root non-empty visible categories join with 'virtual' sale category
        # except categories shown in header
        roots = Category.objects.filter(
            parent=None, visibility=True, show_at_header=False
        ).filter(Q(products__in_stock=True) | Q(products__show_after_sale=True))
        if Product.objects.filter(in_stock=True, discount__gt=0).exists():
            # don't change .filter to .get - it doesn't work with .distinct()
            sale = Category.objects.filter(slug='sale', visibility=True)
            roots = roots | sale
        context['roots'] = roots.distinct().order_by('view_priority')

        # constructing text for html <head><title> and for category naming
        if not self.is_main_page and (slug := self.kwargs['slug']):
            demanded_category = Category.objects.get(slug=slug)
            head_title = demanded_category.title
            context['head_tag_title'] = (
                f'Olga Vilnova Lampwork Beads. {head_title}.'
            )

            if slug == 'tutorials':
                context['category_text'] = 'Tutorials and books:'
            else:
                context['category_text'] = f'Beads in category {demanded_category}'

            # determine show or not navigation submenu and active elements
            root = (demanded_category.parent if demanded_category.parent
                    else demanded_category)
            context['active_branch'] = demanded_category
            context['active_root'] = root
            context['branches'] = (
                Category.objects
                .filter(parent=root, visibility=True, show_at_header=False)
                .filter(Q(products__in_stock=True) | Q(products__show_after_sale=True))
                .distinct().order_by('view_priority')
            )

        # in other cases - showing main page and base catalog
        else:
            context['category_text'] = 'All beads'
            context['head_tag_title'] = 'Olga Vilnova Lampwork Beads.'

        # collects 8 items to promo section: firsts 'promoted' items,
        # if missing, trying to get 16 max-priced items and take randoms
        # to combine with promoted. get no errors if not enough items.
        # shuffle result.
        promo_items = Product.objects.filter(
            promoted=True, in_stock=True, reserved=False)
        number_of_promo_items = promo_items.count()
        if number_of_promo_items >= 8:
            promo_items = random.sample(list(promo_items), 8)
        else:
            additional_promo_items = Product.objects.filter(
                promoted=False, in_stock=True, reserved=False
            ).order_by('-base_price')[:16]
            additional_promo_items = random.sample(
                list(additional_promo_items),
                min(len(additional_promo_items), (8-number_of_promo_items)))
            promo_items = list(promo_items) + additional_promo_items
        random.shuffle(promo_items)
        context['promotions'] = promo_items
        return context
