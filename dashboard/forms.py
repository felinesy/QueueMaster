from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Service, Appointment, BusinessHours, ClosedDay
from accounts.models import Staff


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if not isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                existing_class = widget.attrs.get("class", "")
                widget.attrs["class"] = f"form-control {existing_class}".strip()


class ServiceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Service
        fields = "__all__"


class AppointmentForm(BootstrapFormMixin, forms.ModelForm):
    queue_number = forms.IntegerField(required=False, min_value=1)

    class Meta:
        model = Appointment
        fields = ["customer", "staff", "service", "date", "time", "status", "queue_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].widget.attrs["min"] = timezone.localdate().strftime("%Y-%m-%d")
        if self.instance and self.instance.pk:
            self.fields["queue_number"].initial = self.instance.queue_number

    def clean_queue_number(self):
        queue_number = self.cleaned_data.get("queue_number")
        if queue_number is None:
            return queue_number

        same_day = Appointment.objects.filter(date=self.cleaned_data.get("date"), queue_number=queue_number)
        if self.instance and self.instance.pk:
            same_day = same_day.exclude(pk=self.instance.pk)

        if same_day.exists():
            raise ValidationError("This queue number is already assigned for the selected date.")

        return queue_number

    def save(self, commit=True):
        appointment = super().save(commit=False)
        queue_number = self.cleaned_data.get("queue_number")
        date_changed = bool(self.instance and self.instance.pk and self.instance.date != self.cleaned_data.get("date"))

        if date_changed:
            appointment.queue_number = None
        elif queue_number is not None:
            appointment.queue_number = queue_number

        if commit:
            appointment.save()
        return appointment


class BusinessHoursForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = BusinessHours
        fields = ["open_time", "close_time"]
        widgets = {
            "open_time": forms.TimeInput(attrs={"type": "time"}),
            "close_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        open_time = cleaned_data.get("open_time")
        close_time = cleaned_data.get("close_time")

        if open_time and close_time and close_time <= open_time:
            raise ValidationError("Close time must be later than open time.")

        return cleaned_data


class ClosedDayForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ClosedDay
        fields = ["date", "reason"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.TextInput(attrs={"placeholder": "Optional reason"}),
        }


class AdminStaffForm(BootstrapFormMixin, forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    position = forms.CharField(max_length=100)

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
        return Staff.objects.create(user=user, position=self.cleaned_data["position"])


class AdminStaffEditForm(BootstrapFormMixin, forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    position = forms.CharField(max_length=100)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, *args, staff=None, **kwargs):
        self.staff = staff
        super().__init__(*args, **kwargs)
        if staff is not None:
            self.fields["first_name"].initial = staff.user.first_name
            self.fields["last_name"].initial = staff.user.last_name
            self.fields["username"].initial = staff.user.username
            self.fields["email"].initial = staff.user.email
            self.fields["position"].initial = staff.position

    def clean_username(self):
        username = self.cleaned_data["username"]
        existing = User.objects.filter(username=username)
        if self.staff is not None:
            existing = existing.exclude(pk=self.staff.user.pk)
        if existing.exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        existing = User.objects.filter(email=email)
        if self.staff is not None:
            existing = existing.exclude(pk=self.staff.user.pk)
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
        user = self.staff.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        if self.cleaned_data.get("new_password"):
            user.set_password(self.cleaned_data["new_password"])
        user.save()
        self.staff.position = self.cleaned_data["position"]
        self.staff.save(update_fields=["position"])
        return self.staff


class StaffForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Staff
        fields = "__all__"