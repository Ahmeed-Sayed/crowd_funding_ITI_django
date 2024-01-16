from django.utils import timezone
from django.db import models
from accounts.models import UserProfile
from django.core.validators import MaxValueValidator,MinValueValidator
from accounts.models import SoftDeleteModel

class CategoriesModel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TagsModel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ProjectsModel(SoftDeleteModel,models.Model):
    user = models.ForeignKey(
        UserProfile, related_name="projects", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    details = models.TextField(max_length=3000,validators=[MinValueValidator(50)])
    category = models.ManyToManyField(CategoriesModel)
    target = models.IntegerField()
    tags = models.ManyToManyField(TagsModel)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_featured = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class CommentsModel(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    project = models.ForeignKey(
        ProjectsModel, on_delete=models.CASCADE, related_name="comments"
    )

    def __str__(self):
        return f"comment User: {self.user.user.username} || Comment Text: {self.text} || Comment Project: {self.project.title}"


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
    comment = models.ForeignKey(
        CommentsModel, on_delete=models.CASCADE, related_name="reportedComment"
    )

    def __str__(self):
        return f"User {self.user.user.username} report on Project {self.project.title}"


class DonationModel(SoftDeleteModel,models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="donations"
    )
    project = models.ForeignKey(
        ProjectsModel, related_name="donations", on_delete=models.CASCADE
    )
    donation = models.FloatField()
    created_date=models.DateField(default=timezone.now)

    def __self__(self):
        return self.donation
