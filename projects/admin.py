from django.contrib import admin

# Register your models here.
from .models import *

@admin.register(ProjectsModel)
class ProjectsModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_featured', 'start_time', 'end_time')
    list_editable = ('is_featured',)

admin.site.register(CategoriesModel)
admin.site.register(TagsModel)
admin.site.register(CommentsModel)
admin.site.register(UserProjectRating)
admin.site.register(PictuersModel)
admin.site.register(ProjectReportModel)
admin.site.register(CommentReportModel)
admin.site.register(DonationModel)