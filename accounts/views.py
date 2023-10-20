from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .models import UserProfile
from .forms import RegisterForm
from django.contrib import messages


class AccountRegister(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "accounts/accountRegister.html", {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse("accountRegister"))
        print (form.errors)
        messages.warning(request, "invalid data")
        return render(request, "accounts/accountRegister.html")
