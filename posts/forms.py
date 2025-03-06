from django import forms
from django.forms import ModelForm

from .models import Post



class PostCreateForm(ModelForm):
    class Meta:
        model = Post
        fields = ["url", "body", "tags"]
        labels = {"body": "Caption", "tags": "Category"}
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "row": 3,
                    "placeholder": "Add a caption ...",
                    "class": "font1 text-4xl",
                }
            ),
            "url": forms.TextInput(attrs={"placeholder": "Ad url ..."}),
            "tags": forms.CheckboxSelectMultiple(),
        }

    def clean_url(self):
        """Ensure the URL has a valid scheme (http/https)"""
        url = self.cleaned_data.get("url")  # Use .get() to avoid KeyErrors
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url  # Default to https
        return url


class PostEditForm(ModelForm):
    class Meta:
        model = Post
        fields = ["body", "tags"]
        labels = {"body": "", "tags": "Category"}
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3, "class": "font text-4xl"}),
            "tags": forms.CheckboxSelectMultiple(),
        }
