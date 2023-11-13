from django.views.generic import DetailView

from apps.catalog.models import Product, Category

from mixins import CartContentMixin


class ProductView(CartContentMixin, DetailView):
    model = Product

    def get_template_names(self):
        product = self.get_object()
        if product.category.filter(slug='tutorials').exists():
            return ['tutorial.html']
        return ['product.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        head_title = Product.objects.get(slug=self.kwargs["slug"]).title
        context['head_tag_title'] = f'Olga Vilnova Lampwork. {head_title}.'

        roots = Category.objects.filter(
            parent=None, products__isnull=False, visibility=True
        )
        if Product.objects.filter(in_stock=True, discount__gt=0).exists():
            # don't change .filter to .get - it doesn't work with .distinct()
            sale = Category.objects.filter(slug='sale', visibility=True)
            roots = roots | sale
        context['roots'] = roots.distinct().order_by('view_priority')
        return context
