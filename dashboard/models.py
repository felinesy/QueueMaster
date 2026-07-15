import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from accounts.models import Customer, Staff
from .services import next_queue_number_for_date

class Service(models.Model):
    service_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()

    def __str__(self):
        return self.service_name


class BusinessHours(models.Model):
    open_time = models.TimeField(default=datetime.time(9, 0))
    close_time = models.TimeField(default=datetime.time(17, 0))

    class Meta:
        verbose_name = "Business Hours"
        verbose_name_plural = "Business Hours"

    def clean(self):
        if self.close_time <= self.open_time:
            raise ValidationError({
                "close_time": "Close time must be later than open time."
            })

    def __str__(self):
        return f"{self.open_time.strftime('%H:%M')} - {self.close_time.strftime('%H:%M')}"


class ClosedDay(models.Model):
    date = models.DateField(unique=True)
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        reason = f" ({self.reason})" if self.reason else ""
        return f"{self.date}{reason}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Waiting", "Waiting"),
        ("Serving", "Serving"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    queue_number = models.PositiveIntegerField(null=True, blank=True, editable=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["date", "queue_number", "time"]
        constraints = [
            models.UniqueConstraint(
                fields=["date", "queue_number"],
                name="unique_queue_number_per_day",
            )
        ]

    def __str__(self):
        return f"{self.customer} - {self.service}"

    def save(self, *args, **kwargs):
        previous_date = None
        previous_queue = None
        if self.pk:
            previous_record = Appointment.objects.filter(pk=self.pk).values_list("date", "queue_number").first()
            if previous_record:
                previous_date, previous_queue = previous_record

        if self.pk and previous_date and previous_date != self.date and previous_queue is not None:
            self.queue_number = None

        if not self.queue_number:
            self.queue_number = next_queue_number_for_date(self.date)

        super().save(*args, **kwargs)