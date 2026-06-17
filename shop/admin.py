from django.contrib import admin
from .models import Category, Product, Review


admin.site.register(Category)
admin.site.register(Product)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display= (
        'product',
        'user',
        'rating',
        'created',
        'updated'
    )

    list_filter = (
        'rating',
        'created'
    )

    search_fields = (
        'product__name',
        'user__username'
    )

