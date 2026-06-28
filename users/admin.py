from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Profile, WishlistItem

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'first_name',
        'last_name',
        'email',
        'phone',
        'city',
        'country',
    )

    search_fields = (
        'user__username',
        'user__email',
        'first_name',
        'last_name',
        'phone',
        'city',
    )

    def email(self, obj):
        return obj.user.email
    
    email.short_description = "Email"


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'product',
        'created_at',
    )

    list_filter = (
        'created_at',
    )

    search_fields = (
        'user__username',
        'product__name',
    )

admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
        'date_joined',
    )

    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined',
    )

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    ordering = (
        'username',
    )
