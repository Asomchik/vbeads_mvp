"""
Base Category model for catalog of web shop
"""
from django.db import models
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    """ Model of products category (tree based on mptt package)"""
    title = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey(
        'self', on_delete=models.PROTECT, null=True, blank=True, db_index=True)
    slug = models.SlugField(max_length=150, blank=False, unique=True)
    # sorting parameter for ordering display of categories
    view_priority = models.IntegerField(
        default=1000, blank=False, verbose_name='Display order')
    # enable hide (no-display) option for category
    visibility = models.BooleanField(default=True, blank=False)

    # where to show category True-> at header, False-> in root
    show_at_header = models.BooleanField(default=False, blank=False)

    def get_absolute_url(self):
        return reverse('category', args=[str(self.slug)])

    def __str__(self):
        return str(self.title)

    class MPTTMeta:
        """metaclass for mptt model"""
        order_insertion_by = ['visibility', 'view_priority', 'title']

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
