from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Customer
from dashboard.models import Appointment, Service
from dashboard.services import get_business_hours, is_closed_date


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if not isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                existing_class = widget.attrs.get("class", "")
                widget.attrs["class"] = f"form-control {existing_class}".strip()


class AdminCustomerForm(BootstrapFormMixin, forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    address = forms.CharField(max_length=255, required=False)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )
        return Customer.objects.create(user=user, address=self.cleaned_data.get("address", ""))


class AdminCustomerEditForm(BootstrapFormMixin, forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    address = forms.CharField(max_length=255, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, *args, customer=None, **kwargs):
        self.customer = customer
        super().__init__(*args, **kwargs)
        if customer is not None:
            self.fields["first_name"].initial = customer.user.first_name
            self.fields["last_name"].initial = customer.user.last_name
            self.fields["username"].initial = customer.user.username
            self.fields["email"].initial = customer.user.email
            self.fields["address"].initial = customer.address

    def clean_username(self):
        username = self.cleaned_data["username"]
        existing = User.objects.filter(username=username)
        if self.customer is not None:
            existing = existing.exclude(pk=self.customer.user.pk)
        if existing.exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        existing = User.objects.filter(email=email)
        if self.customer is not None:
            existing = existing.exclude(pk=self.customer.user.pk)
        if existing.exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password", "")
        confirm_password = cleaned_data.get("confirm_password", "")
        if new_password and new_password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self):
        user = self.customer.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        if self.cleaned_data.get("new_password"):
            user.set_password(self.cleaned_data["new_password"])
        user.save()
        self.customer.address = self.cleaned_data.get("address", "")
        self.customer.save(update_fields=["address"])
        return self.customer


class CustomerForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"


class CustomerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update({"class": "form-control", "placeholder": "First name"})
        self.fields["last_name"].widget.attrs.update({"class": "form-control", "placeholder": "Last name"})
        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "Email address"})


class CustomerAppointmentBaseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["service", "date", "time"]
        widgets = {
            "service": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].widget.attrs["min"] = timezone.localdate().strftime("%Y-%m-%d")
        business_hours = get_business_hours()
        time_widget = self.fields["time"].widget
        time_widget.attrs.update({
            "min": business_hours.open_time.strftime("%H:%M"),
            "max": business_hours.close_time.strftime("%H:%M"),
        })

    def clean(self):
        cleaned_data = super().clean()
        selected_date = cleaned_data.get("date")
        selected_time = cleaned_data.get("time")
        business_hours = get_business_hours()

        if selected_date and is_closed_date(selected_date):
            raise ValidationError("This date is closed. Please choose another day.")

        if selected_time:
            if selected_time < business_hours.open_time or selected_time > business_hours.close_time:
                raise ValidationError(
                    f"Please choose a time between {business_hours.open_time.strftime('%H:%M')} and {business_hours.close_time.strftime('%H:%M')}.")

        return cleaned_data


class CustomerAppointmentForm(CustomerAppointmentBaseForm):
    pass


class CustomerAppointmentEditForm(CustomerAppointmentBaseForm):
    pass