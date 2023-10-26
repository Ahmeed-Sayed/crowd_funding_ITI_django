from django.urls import path
from . import views
from . import views

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("project-list", views.project_list, name="home"),
    path("create/", views.CreateProject.as_view(), name="createProject"),
    path("<int:id>/projectDetails/",views.ProjectDetailsView.as_view(),name="projectDetails",),
    path("<int:id>/projectDetails/report-comment/<int:commentID>",views.reportComment,name="reportComment",),

    # path('/<int:id>/edit',editProject,name='editProject'),
    # path('/<int:id>/delete',deleteProject,name='deleteProject'),
    # path('/<int:id>/add-comment',addComment,name='addComment'),
    # path('/<int:id>/add-comment',addComment,name='addComment'),
]
