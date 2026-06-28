from django.db import models
from django.contrib.auth.models import User
from shop.models import Product

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE
    )

    first_name = models.CharField(
        max_length = 100,
        blank = True
    )
    last_name = models.CharField(
        max_length = 100,
        blank = True
    )

    phone = models.CharField(
        max_length = 30,
        blank = True
    )

    country = models.CharField(
        max_length = 100,
        blank = True
    )

    address = models.CharField(
        max_length = 255,
        blank = True
    )

    city = models.CharField(
        max_length = 100,
        blank = True
    )

    postal_code = models.CharField(
        max_length = 20,
        blank = True
    )


    def __str__(self):
        return f'{self.user.username} profile'
    


class WishlistItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlisted_by'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __stra__(self):
        return f"{self.user.username} - {self.product.name}"
