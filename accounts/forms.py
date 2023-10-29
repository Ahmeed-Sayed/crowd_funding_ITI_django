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
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "phoneNumber",
            "password2",
            "image",
        )
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
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
        phone_number = self.cleaned_data["phoneNumber"]
        
        if UserProfile.objects.filter(phoneNumber=phone_number).exists():
            self.add_error('phoneNumber', 'This phone number is already in use.')
            return None

        user_profile = UserProfile(
            user=user,
            phoneNumber=phone_number,
            image=self.cleaned_data["image"],
        )
        if commit:
            user.save()
            user_profile.save()
        return user, user_profile


class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))

    class Meta:
        model = UserProfile
        fields = (
            "username",
            "first_name",
            "last_name",
            "phoneNumber",
            "birthdate",
            "address",
            "image",
        )

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.fields["username"].initial = self.instance.user.username
        self.fields["first_name"].initial = self.instance.user.first_name
        self.fields["last_name"].initial = self.instance.user.last_name
        self.fields["email"].initial = self.instance.user.email
        self.fields["phoneNumber"].widget = forms.TextInput(
            attrs={"class": "form-control"}
        )
        self.fields["image"].widget = forms.FileInput(attrs={"class": "form-control"})
        self.fields["birthdate"].widget = forms.DateInput(
            attrs={"class": "form-control", "type": "date"}
        )
        self.fields["address"].widget = forms.TextInput(attrs={"class": "form-control"})
    def save(self, commit=True):
        user = super(ProfileEditForm, self).save(commit=False)
        user.user.username = self.cleaned_data["username"]
        user.user.first_name = self.cleaned_data["first_name"]
        user.user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.user.save()
            user.save()

        return user
