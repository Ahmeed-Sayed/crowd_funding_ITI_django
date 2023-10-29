from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views import View
from accounts.models import UserProfile
from .models import (
    ProjectsModel,
    CommentsModel,
    UserProjectRating,
    CommentReportModel,
    CategoriesModel,
    ProjectReportModel,
    DonationModel,
)
from django.contrib import messages
from django.db.models import Avg, Sum
from django import forms
from django.db.models import Q

# Create your views here.
from .forms import (
    ProjectCreationForm,
    CommentForm,
    RatingForm,
    DonationForm,
    PictureForm,
    ProjectSearchForm,
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
    top_projects = (
        ProjectsModel.objects.all()
        .annotate(avg_rating=Avg("ratings__rating"))
        .order_by("-avg_rating")[:5]
    )
    for project in top_projects:
        project.total_donations = DonationModel.objects.filter(
            project=project
        ).aggregate(sum=Sum("donation"))["sum"]
        if project.total_donations is None:
            project.total_donations = 0
        project.progress = (project.total_donations / project.target) * 100

    latest_projects = ProjectsModel.objects.all().order_by("-start_time")[:5]
    featured_projects = ProjectsModel.objects.filter(is_featured=True).order_by(
        "-start_time"
    )[:5]
    search_form = ProjectSearchForm(request.GET)
    message = ""
    categories = CategoriesModel.objects.all()
    category_projects = {}

    if search_form.is_valid():
        query = search_form.cleaned_data.get("query")
        print(f"Query: {query}")

        if query:
            projects = ProjectsModel.objects.filter(
                Q(title__icontains=query) | Q(tags__name__icontains=query)
            )
            print(f"Projects: {projects}")
            if projects:
                for category in categories:
                    category_projects[category] = projects.filter(category=category)
            else:
                message = "The project doesn't exist."
        else:
            message = "No query provided."
        print(f"Message: {message}")


    
    return render(
        request,
        "projects/home.html",
        {
            "top_projects": top_projects,
            "latest_projects": latest_projects,
            "featured_projects": featured_projects,
            "categories": categories,
            "search_form": search_form,
            "message": message,
        },
    )


def project_list(request):
    projects = ProjectsModel.objects.all()
    return render(request, "projects/project_list.html", {"projects": projects})


def category_projects(request, category_id):
    category = CategoriesModel.objects.get(pk=category_id)
    projects = ProjectsModel.objects.filter(category=category)
    return render(
        request,
        "projects/category_projects.html",
        {"category": category, "projects": projects},
    )


class CreateProject(View):
    def get(self, request, *args, **kwargs):
        if "profileId" not in request.session:
            return redirect(reverse("accountLogin"))
        project_form = ProjectCreationForm()
        picture_formset = PictureFormSet(prefix="pictures")
        return render(
            request,
            "projects/create.html",
            {"project_form": project_form, "picture_formset": picture_formset},
        )

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
            if donation_amount < 0:
                messages.error(request, "Error, donation amount cannot be negative.")
            elif donation_amount > currentProject.target - total_donations:
                messages.error(
                    request,
                    f"Error, donation amount cannot exceed the remaining target amount. You can donate {currentProject.target-total_donations}$",
                )
            elif total_donations < currentProject.target:
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
            if ratingForm.is_valid():
                if currentUser != currentProject.user:
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
                        "You can't rate your own project",
                    )

            else:
                messages.error(
                    request,
                    "Error, Failed to add rating to project, rating must be between 1-5",
                )

        if request.POST.get("text"):
            if commentForm.is_valid() and commentForm.cleaned_data["text"]:
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
    if currentUser == currentComment.user:
        messages.error(request, "You can't report your own comment.")
        return redirect("projectDetails", id=id)
    existingReport = CommentReportModel.objects.filter(
        user=currentUser, comment=currentComment
    ).first()
    if existingReport:
        messages.info(request, "You have already reported this comment.")
        return redirect("projectDetails", id=id)
    CommentReportModel.objects.create(
        user=currentUser, project=currentProject, comment=currentComment
    )
    return redirect("projectDetails", id=id)


def reportProject(request, id):
    if "profileId" not in request.session:
        return redirect(reverse("accountLogin"))
    currentProject = get_object_or_404(ProjectsModel, id=id)
    currentUser = get_object_or_404(UserProfile, id=request.session["profileId"])
    if currentProject.user.id == request.session["profileId"]:
        messages.info(request, "You Can't Report your own project")
        return redirect("projectDetails", id=id)
    existingReport = ProjectReportModel.objects.filter(
        user=currentUser, project=currentProject
    ).first()
    if existingReport:
        messages.info(request, "You have already reported this comment.")
        return redirect("projectDetails", id=id)
    ProjectReportModel.objects.create(user=currentUser, project=currentProject)
    return redirect("projectDetails", id=id)


def deleteProject(request, id):
    if "profileId" not in request.session:
        return redirect(reverse("accountLogin"))
    currentUser = get_object_or_404(UserProfile, id=request.session["profileId"])
    currentProject = get_object_or_404(ProjectsModel, id=id)
    if currentProject.user.id != request.session["profileId"]:
        messages.info(request, "Only the project creator can delete the project")
        return redirect("projectDetails", id=id)
    total_donations = sum(
        donation.donation for donation in currentProject.donations.all()
    )
    if total_donations >= currentProject.target * 0.25:
        messages.info(
            request,
            "Project donations has passed 25% of the target, you can't delete the project",
        )
        return redirect("projectDetails", id=id)
    return redirect("home")
