from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(CategoriesModel)
admin.site.register(TagsModel)
admin.site.register(ProjectsModel)
admin.site.register(CommentsModel)
admin.site.register(UserProjectRating)
admin.site.register(PictuersModel)
admin.site.register(ProjectReportModel)
admin.site.register(CommentReportModel)
admin.site.register(DonationModel)