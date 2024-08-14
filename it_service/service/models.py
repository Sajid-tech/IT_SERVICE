from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Service(models.Model):
    name = models.CharField(max_length=100)
    payment_terms = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    package = models.CharField(max_length=100)
    tax = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='services/')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    @property
    def total_price(self):
        return self.price + (self.price * self.tax / 100)


class Subscription(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50)
    transaction_details = models.TextField()

    def __str__(self):
        return f'Subscription by {self.user} for {self.service.name}'