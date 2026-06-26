from django.db import models
from shop.models import Product

class CompatibilityRule(models.Model):

    COMPATIBILITY_TYPES = [
        ('CPU_MB', 'CPU -> Motherboard'),
        ('RAM_MB', 'RAM -> Motherboard'),
        ('SSD_MB', 'SSD -> Motherboard'),
        ('GPU_PSU', 'GPU -> PSU'),
        ('GPU_CASE', 'GPU -> Case'),
        ('MB_CASE', 'Motherboard -> Case')
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='compatibility_rules'
    )

    compatible_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='compatible_with'
    )

    compatibility_type = models.CharField(
        max_length=20,
        choices=COMPATIBILITY_TYPES
    )

    class Meta:
        unique_together = (
            'product',
            'compatible_product',
            'compatibility_type'
        )

    def __str__(self):
        return(
            f"{self.product.name} -> "
            f"{self.compatible_product.name} "
            f"({self.get_compatibility_type_display()})"
        )