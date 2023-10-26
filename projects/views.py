from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views import View
from accounts.models import UserProfile
from .models import ProjectsModel, CommentsModel, UserProjectRating, CommentReportModel
from django.contrib import messages
from django.db.models import Avg
from django import forms

# Create your views here.
from .forms import (
    ProjectCreationForm,
    CommentForm,
    RatingForm,
    DonationForm,
    PictureForm,
)


class BasePictureFormSet(forms.BaseFormSet):
    def clean(self):
        super().clean()

        uploaded_pictures = len([form for form in self.forms if form.cleaned_data])
        if uploaded_pictures < 5:
            raise forms.ValidationError("You must upload at least 5 pictures.")


PictureFormSet = forms.formset_factory(
    PictureForm, extra=0, min_num=5, formset=BasePictureFormSet
)


def home(request):
    top_projects = ProjectsModel.objects.filter(completed=True).annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')[:5]
    latest_projects = ProjectsModel.objects.filter(completed=True).order_by('-start_time')[:5]
    featured_projects = ProjectsModel.objects.filter(is_featured=True).order_by('-start_time')[:5]

    return render(request, 'projects/home.html',
                   {'top_projects': top_projects,
                    'latest_projects': latest_projects,
                    'featured_projects': featured_projects})

def project_list(request):
    projects = ProjectsModel.objects.all()  # Fetch all projects
    return render(request, "projects/project_list.html", {"projects": projects})

# class CreateProject(View):
#     def get(self, request, *args, **kwargs):
#         if "profileId" not in request.session:
#             return redirect(reverse("accountLogin"))
#         form = ProjectCreationForm()
#         return render(request, "projects/create.html", {"form": form})

    def post(self, request, *args, **kwargs):
        if "profileId" not in request.session:
            return redirect(reverse("accountLogin"))
        project_form = ProjectCreationForm(request.POST)
        picture_formset = PictureFormSet(request.POST, request.FILES, prefix="pictures")
        if not project_form.is_valid():
            print(project_form.errors)
        if not picture_formset.is_valid():
            print(picture_formset.errors)

        if project_form.is_valid() and picture_formset.is_valid():
            project = project_form.save(commit=False)
            project.user = UserProfile.objects.get(id=request.session["profileId"])
            project.save()

            for picture_form in picture_formset:
                picture = picture_form.save(commit=False)
                picture.project = project
                picture.save()

            return redirect(reverse("createProject"))
        else:
            return render(
                request,
                "projects/create.html",
                {"project_form": project_form, "picture_formset": picture_formset},
            )


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
        commentForm = CommentForm(request.POST or None)
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
                messages.error(
                    request,
                    "Error, Failed to add rating to project,rating must be between 1-5 and you can't rate your project",
                )

        if request.POST.get("text"):
            if commentForm.is_valid():
                newComment = commentForm.save(commit=False)
                newComment.project = currentProject
                newComment.user = currentUser
                newComment.save()
            else:
                messages.error(request, "Error, Failed to add comment to project")
        return redirect("projectDetails", id=id)


def reportComment(request, id, commentID):
    if "profileId" not in request.session:
        return redirect(reverse("accountLogin"))
    currentProject = get_object_or_404(ProjectsModel, id=id)
    currentComment = get_object_or_404(CommentsModel, id=commentID)
    currentUser = get_object_or_404(UserProfile, id=request.session["profileId"])
    existingReport = CommentReportModel.objects.filter(
        user=currentUser, comment=currentComment
    ).first()
    if existingReport:
        messages.info(request, "You have already reported this comment.")
        return redirect("projectDetails", id=id)
    newReport = CommentReportModel.objects.create(
        user=currentUser, project=currentProject, comment=currentComment
    )
    return redirect("projectDetails", id=id)
