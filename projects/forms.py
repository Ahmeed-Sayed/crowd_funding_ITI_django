from django import forms
from .models import ProjectsModel, UserProjectRating, CommentsModel,DonationModel


class ProjectCreationForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        ),
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        ),
    )

    class Meta:
        model = ProjectsModel
        exclude = ("donations", "user")

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
        fields = ['rating']
    def __init__(self, *args, **kwargs):
        super(RatingForm, self).__init__(*args, **kwargs)
        self.fields["rating"].widget = forms.NumberInput(attrs={"class": "form-control"})

class DonationForm(forms.ModelForm):
    class Meta:
        model=DonationModel
        fields=('donation',)
    def __init__(self, *args, **kwargs):
        super(DonationForm, self).__init__(*args, **kwargs)
        self.fields["donation"].widget = forms.NumberInput(attrs={"class": "form-control"})
