from django.contrib import admin
from .models import UserCart, UserCartItem


class UserCartItemInline(admin.TabularInline):
    model = UserCartItem
    extra = 0
    raw_id_fields = ['product']

@admin.register(UserCart)
class UserCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    inlines = [UserCartItemInline]

@admin.register(UserCartItem)
class UserCartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity']
    search_fields = ['cart__user__username', 'product__name']
    list_filter = ['cart']