from django.db import models
from django.contrib.auth.models import User

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
