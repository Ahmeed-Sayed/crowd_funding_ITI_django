from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.views import View
from .models import UserProfile
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm


class AccountRegister(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "accounts/accountRegister.html", {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse("accountRegister"))
        print(form.errors)
        messages.warning(request, "invalid data")
        return render(request, "accounts/accountRegister.html")


class AccountLogin(View):
    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        return render(request, "accounts/accountLogin.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request,request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse("accountRegister"))
        return HttpResponse("not valid")


def AccountLogout(request):
    logout(request)
    return redirect(reverse("accountRegister"))