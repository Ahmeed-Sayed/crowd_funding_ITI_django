from django.urls import path
from .views import *
urlpatterns =[

# path('',home,name='home'),
path('create/',CreateProject.as_view(),name='createProject'),
# path('/<int:id>/edit',editProject,name='editProject'),
# path('/<int:id>/delete',deleteProject,name='deleteProject'),
# path('/<int:id>/add-comment',addComment,name='addComment'),
# path('/<int:id>/add-comment',addComment,name='addComment'),



]