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
        'brand',
        'category',
        'price',
        'discount_percent',
        'stock',
        'socket',
        'ram_type',
        'storage_type',
    )

    list_filter = (
        'category', 
        'brand',
        'socket',
        'ram_type',
        'storage_type',
        'nvme_support',
        'discount_percent',
    )

    search_fields = (
        'name', 
        'brand',
        'model_number',
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
        'user',
        'product',
        'rating',
        'created',
    )

    search_fields = (
        'product__name',
        'user__username'
    )

