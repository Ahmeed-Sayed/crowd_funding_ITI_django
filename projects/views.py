from django.shortcuts import render, reverse, redirect
from django.views import View
from accounts.models import UserProfile
from .models import ProjectsModel, CommentsModel, UserProjectRating
from django.contrib import messages

# Create your views here.
from .forms import ProjectCreationForm, CommentForm, RatingForm


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
            project.save()  # (Now save the form
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
        projectRatings = currentProject.ratings.all()
        return render(
            request,
            "projects/projectDetails.html",
            {
                "commentForm": commentForm,
                "currentProject": currentProject,
                "projectComments": projectComments,
                "ratingForm": ratingForm,
                "projectRatings": projectRatings,
            },
        )

    def post(self, request, *args, **kwargs):
        id = kwargs.pop("id")
        currentProject = ProjectsModel.objects.get(id=id)
        commentForm = CommentForm(request.POST or None)
        ratingForm = RatingForm(request.POST or None)
        currentUser = UserProfile.objects.get(id=request.session["profileId"])
        if request.POST.get('comment'):
         if commentForm.is_valid():
             newComment = commentForm.save(commit=False)
             newComment.project = currentProject
             newComment.user = currentUser
             newComment.save()
         else:
             messages.error(request, "Error in comment form")

        if request.POST.get("rating"):
            if (
                ratingForm.is_valid() and currentUser != currentProject.user
            ):  # Check if the user is not the project owner
                # Check if a rating from this user for this project already exists
                existingRating = UserProjectRating.objects.filter(
                    user=currentUser, project=currentProject
                ).first()
                if existingRating:
                    # If it does, update the existing rating
                    existingRating.rating = ratingForm.cleaned_data["rating"]
                    existingRating.save()
                else:
                    # If it doesn't, create a new rating
                    newRating = ratingForm.save(commit=False)
                    newRating.project = currentProject
                    newRating.user = currentUser
                    newRating.save()
            else:
                messages.error(request, "Error in rating form")

        return redirect("projectDetails", id=id)
