from django import forms
from .models import Service, Appointment
from accounts.models import Staff

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = "__all__"


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = "__all__"


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = "__all__"