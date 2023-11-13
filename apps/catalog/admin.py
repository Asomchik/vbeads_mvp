"""
Admin pages for Product and Category
"""
from django import forms
from django.db import models
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from mptt.admin import MPTTModelAdmin, TreeRelatedFieldListFilter
from easy_thumbnails.templatetags.thumbnail import thumbnail_url

from apps.catalog.models import Product, Category

admin.site.site_title = "V.Olga Beads"
admin.site.site_header = "V.Olga Beads"


class UpdateActionForm(ActionForm):
    """Add custom form fields for actions"""
    price = forms.IntegerField(required=False, label='New price')
    discount = forms.IntegerField(required=False, label='Discount')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Custom Product list and form admin pages"""
    # change some css for better view
    class Media:
        css = {
            'all': ['product_admin_page.css']
        }

    # add buttons for custom actions on the change Order instance page
    change_list_template = 'for_admin/edit_list_of_orders.html'

    # add custom fields to action
    action_form = UpdateActionForm

    # list appearance
    list_display = ('get_main_image', 'title', 'base_price', 'discount', 'price',
                    'show_after_sale', 'in_stock', 'reserved', 'promoted',
                    'view_creation_date')
    list_display_links = ('title',)
    list_editable = ('base_price', 'discount', 'show_after_sale', 'promoted',
                     'in_stock', 'reserved')
    list_filter = ('show_after_sale', 'in_stock', 'reserved', 'discount',
                   ('category', TreeRelatedFieldListFilter),
                   )
    search_fields = ('title',)
    ordering = ['show_after_sale', '-created_at', 'title']

    # instance appearance
    save_on_top = True
    save_as = True
    filter_horizontal = ('category',)
    prepopulated_fields = {"slug": ("title",)}

    # small changes to some fields view
    formfield_overrides = {
        models.CharField: {
            'widget': forms.TextInput(attrs={'size': '30'})
        },
        models.TextField: {
            'widget': forms.Textarea(attrs={'rows': 3, 'cols': 30})
        }
    }

    readonly_fields = (
        'created_at', 'get_all_images', 'price', 'view_creation_date',
        'display_size', 'draw_category_tree'
    )

    fieldsets = [
        (
            ' ',
            {
                'fields': [
                    ('title', 'slug', 'description'),
                    ('show_after_sale', 'in_stock', 'reserved', 'view_creation_date')
                ],
            }
        ),

        (
            ' ',
            {
                'fields': [
                    ('base_price', 'discount', 'price'),
                    ('size_1', 'size_2', 'size_3', 'display_size'),
                    ('hole_position', 'hole_size'),
                    ('category', 'draw_category_tree'),
                ],
            }
        ),
        (
            'Photos',
            {
                'fields': [
                    ('picture_1', 'get_all_images'),
                    'picture_2',
                    'picture_3',
                    'picture_4',
                    'picture_5',
                    'link_to_video',
                ],
                'classes': ['some_class', ],
                'description': ['short or not description', ],

            }
        ),

    ]

    def view_creation_date(self, obj):
        """show human-readable date at list page"""
        return obj.created_at.strftime('%Y-%m-%d')
    view_creation_date.short_description = 'Created'

    def get_main_image(self, obj):
        """show image of Product at list page"""
        return mark_safe(self._generate_html_for_image_field(obj.picture_1))
    get_main_image.short_description = "Main picture"

    def get_all_images(self, obj):
        """show images of Product at change page"""
        html_for_images = (
                self._generate_html_for_image_field(obj.picture_1) +
                self._generate_html_for_image_field(obj.picture_2) +
                self._generate_html_for_image_field(obj.picture_3) +
                self._generate_html_for_image_field(obj.picture_4) +
                self._generate_html_for_image_field(obj.picture_5)
        )
        return mark_safe(html_for_images)
    get_all_images.short_description = "Pictures"

    def _generate_html_for_image_field(self, img_field):
        """html for thumbnail pictures of product with :hover resize"""
        if not img_field:
            return ''
        url_small = thumbnail_url(img_field, 'small')
        url_medium = thumbnail_url(img_field, 'medium')
        return (f'<div class="admin-image-container">'
                f'<img class="small-image" src={url_small} alt="small-img">'
                f'<img class="medium-image" src={url_medium} alt="medium-img">'
                '</div>'
                )

    def draw_category_tree(self, obj):
        """show category tree at change page for convenience (mptt based)"""
        nodes = Category.objects.all()
        return render_to_string(
            "for_admin/construct_category_tree.html", {'nodes': nodes})


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    """Custom Category list and form admin pages"""
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'view_priority', 'visibility', 'slug',
                    'show_at_header')
    search_fields = ('title',)
    list_filter = ('visibility', 'title', 'show_at_header')
    list_editable = ('view_priority', 'visibility', 'show_at_header')

    class Meta:
        verbose_name_plural = 'Categories'
