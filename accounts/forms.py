from django import forms
from .models import Customer, User

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"