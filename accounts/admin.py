from django.contrib import admin
from .models import Role, User, Customer, Staff, Notification

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Staff)
admin.site.register(Notification)
