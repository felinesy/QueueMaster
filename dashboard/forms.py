from django import forms
from .models import Service, Appointment


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = "__all__"


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = "__all__"