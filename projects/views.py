from django.shortcuts import render, reverse, redirect
from django.views import View
from accounts.models import UserProfile

# Create your views here.
from .forms import ProjectCreationForm


class CreateProject(View):
    def get(self, request, *args, **kwargs):
        if "profileId" not in request.session:
            return redirect(reverse("accountLogin"))
        form = ProjectCreationForm()
        return render(request, "projects/create.html", {"form": form})

    def post(self, request, *args, **kwargs):
        if "profileId" not in request.session:
            return redirect(reverse("accountLogin"))
        form = ProjectCreationForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)  # Don't save the form yet
            project.user = UserProfile.objects.get(
                id=request.session["profileId"]
            )  # Set the user field
            project.save()  # Now save the form
            return redirect(reverse("createProject"))
        else:
            return render(request, "projects/create.html", {"form": form})
