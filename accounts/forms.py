from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile
import re


def validate_phone_number(value):
    pattern = r"^(011|012|010|015)\d{8}$"
    if not re.match(pattern, value):
        raise ValidationError(
            "Phone number must start with 011, 012, 010, or 015 and be 11 digits long."
        )


class RegisterForm(UserCreationForm):
    phoneNumber = forms.CharField(
        max_length=20,
        validators=[validate_phone_number],
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    image = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ("username", "email", "phoneNumber", "password1", "password2", "image")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={"class": "form-control"}
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={"class": "form-control"}
        )

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user_profile = UserProfile(
            user=user,
            phoneNumber=self.cleaned_data["phoneNumber"],
            image=self.cleaned_data["image"],
        )
        if commit:
            user.save()
            user_profile.save()
        return user, user_profile
