from django.shortcuts import render, reverse, redirect
from django.views import View
from accounts.models import UserProfile
from .models import ProjectsModel, CommentsModel

# Create your views here.
from .forms import ProjectCreationForm, CommentForm


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
        projectComments = currentProject.comments.all()
        commentForm = CommentForm()
        return render(
            request,
            "projects/projectDetails.html",
            {
                "commentForm": commentForm,
                "currentProject": currentProject,
                "projectComments": projectComments,
            },
        )
    def post(self,request, *args, **kwargs):
        id = kwargs.pop("id")
        currentProject = ProjectsModel.objects.get(id=id)
        commentForm=CommentForm(request.POST)
        projectComments=currentProject.comments.all()    
        currentUser=UserProfile.objects.get(id=request.session["profileId"])
        if commentForm.is_valid():
            newComment=commentForm.save(commit=False)
            newComment.project=currentProject
            newComment.user=currentUser
            newComment.save()
            return redirect('projectDetails',id=id)    
        return render(request, 'projects/projectDetails.html',{
                "commentForm": commentForm,
                "currentProject": currentProject,
                "projectComments": projectComments,
            },)
    
