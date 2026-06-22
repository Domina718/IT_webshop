from django.contrib import admin
from .models import UserCart, UserCartItem


class UserCartItemInline(admin.TabularInline):
    model = UserCartItem
    extra = 0

@admin.register(UserCart)
class UserCartAdmin(admin.ModelAdmin):
    inlines = [UserCartItemInline]

@admin.register(UserCartItem)
class UserCartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')