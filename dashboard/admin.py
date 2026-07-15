from django.contrib import admin
from .models import Service, Appointment, BusinessHours, ClosedDay

admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(BusinessHours)
admin.site.register(ClosedDay)
