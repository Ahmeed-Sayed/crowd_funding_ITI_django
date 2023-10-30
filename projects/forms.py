from django.utils import timezone
from django import forms
from .models import (
    ProjectsModel,
    UserProjectRating,
    CommentsModel,
    DonationModel,
    PictuersModel,
    CategoriesModel,
    TagsModel
)

from django.core.exceptions import ValidationError
import os
from django.core.files.images import get_image_dimensions


class ProjectCreationForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )
    category = forms.ModelMultipleChoiceField(
        queryset=CategoriesModel.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=TagsModel.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = ProjectsModel
        exclude = ("donations", "user", "completed", "closed")

    def clean_start_time(self):
        start_time = self.cleaned_data.get("start_time")
        if start_time and start_time < timezone.now():
            raise ValidationError("Start date should be today or later.")
        return start_time

    def clean_end_time(self):
        end_time = self.cleaned_data.get("end_time")
        start_time = self.cleaned_data.get("start_time")
        if end_time and start_time and end_time <= start_time:
            raise ValidationError("End date should be after the start date.")
        return end_time

    def clean_target(self):
        target = self.cleaned_data.get('target')
        if target and target <= 0:
            raise ValidationError('Target must be greater than 0.')
        return target  
    
    def __init__(self, *args, **kwargs):
        super(ProjectCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})
      
class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentsModel
        fields = ("text",)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields["text"].widget = forms.TextInput(attrs={"class": "form-control"})


class RatingForm(forms.ModelForm):
    class Meta:
        model = UserProjectRating
        fields = ["rating"]

    def __init__(self, *args, **kwargs):
        super(RatingForm, self).__init__(*args, **kwargs)
        self.fields["rating"].widget = forms.NumberInput(
            attrs={"class": "form-control"}
        )


class DonationForm(forms.ModelForm):
    class Meta:
        model = DonationModel
        fields = ("donation",)

    def __init__(self, *args, **kwargs):
        super(DonationForm, self).__init__(*args, **kwargs)
        self.fields["donation"].widget = forms.NumberInput(
            attrs={"class": "form-control"}
        )


def validate_image_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = [".jpg", ".png", ".jpeg"]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension.")
    w, h = get_image_dimensions(value)
    if w is None:
        raise ValidationError("Invalid image file.")


class PictureForm(forms.ModelForm):
    image = forms.ImageField(
        validators=[validate_image_file_extension],
        error_messages={"required": "You must upload an image."},
    )

    class Meta:
        model = PictuersModel
        fields = ("image",)

    def __init__(self, *args, **kwargs):
        super(PictureForm, self).__init__(*args, **kwargs)
        self.fields["image"].widget = forms.FileInput(attrs={"class": "form-control"})


class ProjectSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)
    def clean_query(self):
        query = self.cleaned_data.get('query')
        if not query or query.isspace():
            raise forms.ValidationError("This field cannot be empty.")
        return query
    def __init__(self, *args, **kwargs):
        super(ProjectSearchForm, self).__init__(*args, **kwargs)
        self.fields["query"].widget = forms.TextInput(attrs={"class": "form-control"})
