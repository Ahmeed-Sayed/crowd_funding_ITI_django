from django.urls import path
from . import views

urlpatterns = [
    path("list-project/", views.project_list, name="project_list"),
    path("", views.home, name="home"),
    path("category/<int:category_id>/", views.category_projects, name="category"
    ),
    path("create/", views.CreateProject.as_view(), name="createProject"),
    path("<int:id>/projectDetails/",views.ProjectDetailsView.as_view(),name="projectDetails",
    ),
     path("<int:id>/projectDetails/report-comment/<int:commentID>",views.reportComment,name="reportComment"),
     path("<int:id>/projectDetails/reportProject",views.reportProject,name="reportProject"),
     path("<int:id>/projectDetails/deleteProject",views.deleteProject,name="deleteProject",),
     path('projectSearch/<str:query>?/', views.searchResults, name="searchResults")
   
]
