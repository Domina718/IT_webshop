from django.contrib import admin
from .models import CompatibilityRule


@admin.register(CompatibilityRule)
class CompatibilityRuleAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'compatible_product',
        'compatibility_type',
    )

    list_filter = (
        'compatibility_type',
    )

    search_fields = (
        'product__name',
        'compatible_product__name',
    )
