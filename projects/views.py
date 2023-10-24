from django.shortcuts import render, reverse, redirect
from django.views import View
from accounts.models import UserProfile
from .models import ProjectsModel, CommentsModel, UserProjectRating
from django.contrib import messages
from django.db.models import Avg

# Create your views here.
from .forms import ProjectCreationForm, CommentForm, RatingForm, DonationForm


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
            project = form.save(commit=False)
            project.user = UserProfile.objects.get(id=request.session["profileId"])
            project.save()
            return redirect(reverse("createProject"))
        else:
            return render(request, "projects/create.html", {"form": form})


class ProjectDetailsView(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.pop("id")
        currentProject = ProjectsModel.objects.get(id=id)
        ratingForm = RatingForm()
        projectComments = currentProject.comments.all()
        commentForm = CommentForm()
        donationForm = DonationForm()
        projectRatings = currentProject.ratings.all()
        averageRating = (
            projectRatings.aggregate(Avg("rating"))["rating__avg"]
            if projectRatings
            else 0
        )
        return render(
            request,
            "projects/projectDetails.html",
            {
                "commentForm": commentForm,
                "currentProject": currentProject,
                "projectComments": projectComments,
                "ratingForm": ratingForm,
                "projectRatings": projectRatings,
                "averageRating": averageRating,
                "donationForm": donationForm,
            },
        )

    def post(self, request, *args, **kwargs):
        id = kwargs.pop("id")
        currentProject = ProjectsModel.objects.get(id=id)
        ratingForm = RatingForm(request.POST or None)
        donationForm = DonationForm(request.POST or None)
        total_donations = sum(
            donation.donation for donation in currentProject.donations.all()
        )
        currentUser = UserProfile.objects.get(id=request.session["profileId"])

        if request.POST.get("donation"):
            donation_amount = float(request.POST.get("donation"))
            if total_donations < currentProject.target:
                if donationForm.is_valid():
                    newDonation = donationForm.save(commit=False)
                    newDonation.project = currentProject
                    newDonation.user = currentUser
                    newDonation.save()
                    total_donations += donation_amount
                    if total_donations >= currentProject.target:
                        currentProject.completed = True
                        currentProject.save()
                else:
                    messages.error(request, "Error, failed to add donation.")
            else:
                messages.error(
                    request,
                    "This project has already reached its target. No more donations are needed.",
                )
        if request.POST.get("rating"):
            if ratingForm.is_valid() and currentUser != currentProject.user:
                existingRating = UserProjectRating.objects.filter(
                    user=currentUser, project=currentProject
                ).first()
                if existingRating:
                    existingRating.rating = ratingForm.cleaned_data["rating"]
                    existingRating.save()
                else:
                    newRating = ratingForm.save(commit=False)
                    newRating.project = currentProject
                    newRating.user = currentUser
                    newRating.save()
            else:
                messages.error(request, "Error, Failed to add rating to project")

        return redirect("projectDetails", id=id)
