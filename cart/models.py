from django.db import models
from django.contrib.auth.models import User
from shop.models import Product

class UserCart(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s cart"
    
class UserCartItem(models.Model):

    cart = models.ForeignKey(
        UserCart,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default = 1
    )

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"