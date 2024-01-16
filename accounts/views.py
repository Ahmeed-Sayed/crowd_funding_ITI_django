from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.urls import reverse
from django.views import View
from .models import UserProfile
from .forms import RegisterForm, ProfileEditForm
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.utils.decorators import method_decorator


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("profileId"):
            return view_func(request, *args, **kwargs)
        else:
            return redirect("accountLogin")

    return wrapper


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
            f"Dear {user}, please go to your email {to_email} inbox and click on \
                received activation link to confirm and complete the registration. Note: Check your spam folder.",
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
            result = form.save(commit=False)
            if result is None:
                return render(request, "accounts/accountRegister.html", {"form": form})

            user, user_profile = result
            user.is_active = False
            user.save()
            user_profile.user = user
            user_profile.save()
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
                profile = UserProfile.objects.get(user=user)
                request.session["username"] = profile.user.username
                request.session["profileId"] = profile.id
                return redirect(reverse("home"))
            else:
                form.add_error(None, "Invalid email or password")
        return render(request, "accounts/accountLogin.html", {"form": form})

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        return render(request, "accounts/accountLogin.html", {"form": form})


@login_required
def accountLogout(request):
    request.session.flush()
    return redirect(reverse("home"))


@login_required
def profileView(request, id):
    if request.session.get("profileId") != id:
        return render(request, "404.html")
    user = get_object_or_404(UserProfile, id=id)
    return render(
        request,
        "accounts/profile.html",
        {
            "user": user,
        },
    )


class ProfileEditView(View):
    @method_decorator(login_required, name="dispatch")
    def get(self, request, *args, **kwargs):
        id = kwargs.pop("id")
        if request.session.get("profileId") != id:
            return render(request, "404.html")
        user = get_object_or_404(UserProfile, id=id)
        form = ProfileEditForm(instance=user, label_suffix="")
        return render(request, "accounts/profileEdit.html", {"form": form})

    @method_decorator(login_required, name="dispatch")
    def post(self, request, *args, **kwargs):
        id = kwargs.pop("id")
        if request.session.get("profileId") != id:
            return render(request, "404.html")
        user = get_object_or_404(UserProfile, id=id)
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect(reverse("profile", args=[user.id]))
        else:
            return render(request, "accounts/profileEdit.html", {"form": form})


@login_required
def profileDelete(request, id):
    if request.method == "POST":
        if request.session.get("profileId") != id:
            return render(request, "404.html")
        profile = get_object_or_404(UserProfile, id=id)
        user = profile.user
        request.session.flush()
        user.delete()
        return redirect(reverse("home"))
    else:
        return None
