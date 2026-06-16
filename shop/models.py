from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Categories"



class Product(models.Model):
    name = models.CharField(max_length = 255)

    description = models.TextField(
        blank = True,
        null = True
    )

    price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2
    )

    category = models.ForeignKey(
        Category,
        on_delete = models.CASCADE
    )

    stock = models.IntegerField(default = 0)

    image = models.ImageField(
        upload_to = 'products/',
        blank = True,
        null = True
    )

    socket = models.CharField(
        max_length = 50,
        blank = True
    )

    ram_type = models.CharField(
        max_length = 50,
        blank = True
    )

    def __str__(self):
        return self.name
    
class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete = models.CASCADE,
        related_name = 'reviews'
    )

    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created']

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"