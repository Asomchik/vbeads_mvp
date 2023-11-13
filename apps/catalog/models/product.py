"""
Base Product model for catalog of web shop
"""
from django.db import models
from django.urls import reverse

from apps.catalog.models import Category


class Product(models.Model):
    """Basic model of product selling in shop"""
    title = models.CharField(max_length=100, blank=False)
    slug = models.SlugField(max_length=150, blank=False, unique=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Created', blank=False)
    category = models.ManyToManyField(
        'Category', related_name='products', blank=False)

    # for displaying on website (even html for some products)
    description = models.TextField(null=True, blank=True)
    # for admins notes
    memo = models.TextField(null=True, blank=True)

    # enable/disable web displaying after sale (when in_stock=False)
    show_after_sale = models.BooleanField(
        default=True, verbose_name='Show sold', blank=False)

    # stock and reserve status
    in_stock = models.BooleanField(default=True, blank=False)
    reserved = models.BooleanField(default=False, blank=False)

    # special status for filling 'promotion' section of website
    promoted = models.BooleanField(default=False, blank=False)

    # base_price - int U$D, discount - int % to minus from base_price
    # price is determined further as @property
    base_price = models.IntegerField(
        default=0, blank=False, verbose_name='Base price')
    discount = models.IntegerField(
        default=0, blank=False, verbose_name='% discount')

    # photos 1(required) + 2-5(optional)
    picture_1 = models.ImageField(upload_to='photos/', null=False, blank=False)
    picture_2 = models.ImageField(upload_to='photos/', null=True, blank=True)
    picture_3 = models.ImageField(upload_to='photos/', null=True, blank=True)
    picture_4 = models.ImageField(upload_to='photos/', null=True, blank=True)
    picture_5 = models.ImageField(upload_to='photos/', null=True, blank=True)

    # video if exists
    link_to_video = models.URLField(null=True, blank=True)

    # size 1(required) + 2-3(optional)
    size_1 = models.IntegerField(default=0, blank=False, verbose_name='Size')
    size_2 = models.IntegerField(null=True, blank=True)
    size_3 = models.IntegerField(null=True, blank=True)

    # hole position, if exists
    HOLES_CHOICES = [
        ('NO', 'No hole'),
        ('HOR', 'horizontal'),
        ('VERT', 'vertical'),
        ('DIAG', 'diagonal')
    ]
    hole_position = models.CharField(
        max_length=5, default='HOR', choices=HOLES_CHOICES)

    # Hole size - mandrel diameter
    MANDRELS_CHOICES = [
        (0, 'No mandrel used'),
        (2, 'd1,6 mm'),
        (3, 'd2 mm'),
        (4, 'd3,2 mm')
    ]
    hole_size = models.SmallIntegerField(default=2, choices=MANDRELS_CHOICES)

    @property
    def price(self):
        """ count current price with discount. No double information in DB"""
        return int(self.base_price * (1 - self.discount / 100))
    price.fget.short_description = 'Price-disc'

    @property
    def display_size(self):
        """ make string of sizes depending on number of provided dimensions"""
        all_sizes = [
            str(x) for x in [self.size_1, self.size_2, self.size_3] if x
        ]
        return 'x'.join(all_sizes) + ' mm'
    display_size.fget.short_description = 'display size'

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('product', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        # make tutorials always available - no 'reserved'

        # save first to be sure to have id for further actions (it's about new)
        super().save(*args, **kwargs)

        # then check categories
        tutorials_category = Category.objects.get(slug='tutorials')
        if tutorials_category in self.category.all():
            # self.in_stock = True
            self.reserved = False
        super().save(*args, **kwargs)

    class Meta:
        """metaclass for Product model"""
        # IMPORTANT this param sets the sorting order for all shop pages
        # first: in_stock - no reserve - youngest
        ordering = ['-in_stock', 'reserved', '-created_at']
