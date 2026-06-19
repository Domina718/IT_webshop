from django.contrib import admin
from .models import Category, Product, Review


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
    )

    inlines = [
        ProductInline,
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'price',
        'stock',
    )

    list_filter = (
        'category', 
        'stock',
    )

    search_fields = (
        'name', 
        'category__name',
    )

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

