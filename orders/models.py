from django.db import models
from django.contrib.auth.models import User
from shop.models import Product

class Order(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete = models.CASCADE,
        related_name = 'orders'
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()

    phone = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=100, blank=True)

    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
    def __str__(self):
        return f"Order #{self.id}"
    
    
                                   

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name = 'items',
        on_delete = models.CASCADE
    )

    product = models.ForeignKey(
        Product, 
        related_name = 'order_items',
        on_delete = models.CASCADE
    )

    price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2
    )

    quantity = models.PositiveIntegerField(default = 1)

    def __str__(self):
        return str(self.id)
    
    def get_cost(self):
        return self.price * self.quantity

