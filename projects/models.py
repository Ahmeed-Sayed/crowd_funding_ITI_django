from django.db import models
from accounts.models import UserProfile
from django.core.validators import MaxValueValidator

class CategoriesModel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TagsModel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ProjectsModel(models.Model):
    user=models.ForeignKey(UserProfile, related_name='projects',on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    details = models.TextField(max_length=500)
    category = models.ManyToManyField(CategoriesModel)
    target = models.IntegerField()
    tags = models.ManyToManyField(TagsModel)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    donations = models.FloatField(default=0)

    def __str__(self):
        return self.title


class CommentsModel(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    project = models.ForeignKey(
        ProjectsModel, on_delete=models.CASCADE, related_name="comments"
    )


class UserProjectRating(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(
        ProjectsModel, on_delete=models.CASCADE, related_name="ratings"
    )
    rating = models.IntegerField(validators=[MaxValueValidator(5)])


class PictuersModel(models.Model):
    image = models.ImageField(upload_to="projectImages")
    project = models.ForeignKey(
        ProjectsModel, related_name="images", on_delete=models.CASCADE
    )


class ProjectReportModel(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(
        ProjectsModel, related_name="projectReports", on_delete=models.CASCADE
    )
    text = models.TextField(max_length=200)


class CommentReportModel(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(
        ProjectsModel, related_name="commentReports", on_delete=models.CASCADE
    )
    text = models.TextField(max_length=200)
