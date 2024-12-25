from django.db import models
from captcha.fields import CaptchaField


class MainComment(models.Model):
    user_name = models.CharField(max_length=100)
    email = models.EmailField()
    home_page = models.URLField(blank=True, null=True)
    text = models.TextField()
    captcha = CaptchaField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)

    def __str__(self):
        return f"Main Comment by {self.user_name} at {self.created_at}"


class Reply(models.Model):
    main_comment = models.ForeignKey(
        MainComment, related_name='replies', on_delete=models.CASCADE
    )
    user_name = models.CharField(max_length=100)
    email = models.EmailField()
    home_page = models.URLField(blank=True, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user_name} to MainComment {self.main_comment.id}"
