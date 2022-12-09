from django import forms
from .models import Comment


class CommentAdminForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ('user', 'event', 'content')