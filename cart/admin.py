from django.contrib import admin
from .models import UserCart, UserCartItem


class UserCartItemInline(admin.TabularInline):
    model = UserCartItem
    extra = 0
    raw_id_fields = ['product']

@admin.register(UserCart)
class UserCartAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'user', 
        'item_count',
        'total_quantity',
        'created_at', 
        'updated_at'
    ]

    search_fields = [
        'user__username',
        'user__email'
    ]

    inlines = [UserCartItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Products'

    def total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())
    total_quantity.short_description = 'Quantity'

@admin.register(UserCartItem)
class UserCartItemAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'cart', 
        'product', 
        'quantity'
    ]

    search_fields = [
        'cart__user__username',
        'product__name'
    ]

    list_filter = ['cart']