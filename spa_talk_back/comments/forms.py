from django import forms
from .models import Comment


class CommentForm(forms.ModelsForm):
    class Meta:
        model = Comment
        fields = ['user_name', 'email', 'home_page', 'text', 'captcha']
        
        
    def clean(self):
        cleaned_data = super().clean()
        
        return cleaned_data