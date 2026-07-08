from django.db import models
from accounts.models import Customer, Staff

class Service(models.Model):
    service_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()

    def __str__(self):
        return self.service_name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("Waiting", "Waiting"),
        ("Serving", "Serving"),
        ("Completed", "Completed"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.customer} - {self.service}"