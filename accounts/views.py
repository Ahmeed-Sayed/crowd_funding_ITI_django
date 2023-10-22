from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.views import View
from .models import UserProfile
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.core.mail import EmailMessage


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(
            request,
            "Thank you for your email confirmation. Now you can login your account.",
        )
        return redirect(reverse("accountLogin"))
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect(reverse("accountRegister"))


def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string(
        "accounts/template_activate_account.html",
        {
            "user": user.username,
            "domain": get_current_site(request).domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
            "protocol": "https" if request.is_secure() else "http",
        },
    )
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(
            request,
            f"Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
                received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.",
        )
    else:
        messages.error(
            request,
            f"Problem sending email to {to_email}, check if you typed it correctly.",
        )


class AccountRegister(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "accounts/accountRegister.html", {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user, user_profile = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data["email"])
            return redirect(reverse("accountRegister"))
        return render(request, "accounts/accountRegister.html", {"form": form})


class AccountLogin(View):
    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                request.session["username"] = user.username
                request.session["userId"] = user.id
                return redirect(reverse("accountRegister"))
            else:
                form.add_error(None, "Invalid email or password")
        return render(request, "accounts/accountLogin.html", {"form": form})

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        return render(request, "accounts/accountLogin.html", {"form": form})


def accountLogout(request):
    request.session.flush()
    return redirect(reverse("accountRegister"))
