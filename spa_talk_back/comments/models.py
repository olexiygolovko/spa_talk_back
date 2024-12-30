from django.contrib.auth.models import User
from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="User")
    photo = models.ImageField(
        upload_to='user_photos/', blank=True, null=True, verbose_name="Profile Photo")
    home_page = models.URLField(
        blank=True, null=True, verbose_name="Personal Home Page")

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts", verbose_name="Author"
    )
    text = models.TextField(verbose_name="Post Content")
    image = models.ImageField(
        upload_to='post_images/', blank=True, null=True, verbose_name="Attached Image")
    file = models.FileField(upload_to='post_files/',
                            blank=True, null=True, verbose_name="Attached File")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Creation Date")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Last Update")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"


class Comment(models.Model):
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE, verbose_name="Related Post"
    )
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name="replies", on_delete=models.CASCADE, verbose_name="Parent Comment"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments", verbose_name="Comment Author"
    )
    text = models.TextField(verbose_name="Comment Text")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Creation Date")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Last Update")
    image = models.ImageField(upload_to='comment_images/',
                              blank=True, null=True, verbose_name="Attached Image")
    file = models.FileField(upload_to='comment_files/',
                            blank=True, null=True, verbose_name="Attached File")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post} at {self.created_at}"

    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent is not None
