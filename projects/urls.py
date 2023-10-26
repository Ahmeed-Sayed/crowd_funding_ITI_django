from django.urls import path
from . import views
urlpatterns =[

    path('list-projects/', views.project_list, name='project_list'),
    path('', views.home, name='home'),
# path('create/',CreateProject.as_view(),name='createProject'),
# path('<int:id>/projectDetails/',ProjectDetailsView.as_view(),name='projectDetails'),
# path('/<int:id>/edit',editProject,name='editProject'),
# path('/<int:id>/delete',deleteProject,name='deleteProject'),
# path('/<int:id>/add-comment',addComment,name='addComment'),
# path('/<int:id>/add-comment',addComment,name='addComment'),



]