from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.core.exceptions import ValidationError
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import sys


# Extending the standard User model, adding additional fields without changing User
class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="User")
    photo = models.ImageField(
        upload_to='user_photos/', blank=True, null=True, verbose_name="Profile Photo")
    home_page = models.URLField(
        blank=True, null=True, verbose_name="Personal Home Page")

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Django signal that is fired after a User is saved.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a profile when creating a user
        Profile.objects.get_or_create(user=instance)
    else:
        instance.profile.save()


# Checks and resizes the uploaded image
def validate_image_size(image):
    if isinstance(image, InMemoryUploadedFile):
        try:
            with Image.open(image) as img:
                if img.height > 240 or img.width > 320:
                    output_size = (320, 240)
                    img.thumbnail(output_size)

                    output = BytesIO()

                    if image.content_type == 'image/jpeg':
                        img.save(output, format='JPEG', quality=85)
                    elif image.content_type == 'image/png':
                        img.save(output, format='PNG')
                    elif image.content_type == 'image/gif':
                        img.save(output, format='GIF')

                    output.seek(0)
                    return InMemoryUploadedFile(
                        output,
                        'ImageField',
                        f"{image.name.split('.')[0]}_resized.{image.name.split('.')[-1]}",
                        image.content_type,
                        output.getbuffer().nbytes,
                        None
                    )
            return image 
        except Exception as e:
            print(f"Error processing image: {e}")
            raise ValidationError("Error processing image file")


# Checks the extension of the file being downloaded
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.txt']
    if ext.lower() not in valid_extensions:
        raise ValidationError('Only TXT files are allowed.')


# Checks the size of the file being uploaded
def validate_file_size(value):
    if value.size > 102400:  # 100kb in bytes
        raise ValidationError('File size cannot exceed 100KB.')


# Post model, main publication
class Post(models.Model):
    # related_name="posts" - allows to get all posts of a user via user.posts ↓
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts", verbose_name="Author"
    )
    text = models.TextField(verbose_name="Post Content")
    image = models.ImageField(
        upload_to='post_images/',
        blank=True,
        null=True,
        validators=[validate_image_size],
        verbose_name="Attached Image"
    )
    file = models.FileField(
        upload_to='post_files/',
        blank=True,
        null=True,
        validators=[validate_file_extension, validate_file_size],
        verbose_name="Attached File"
    )
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

    def save(self, *args, **kwargs):
        if self.image:
            try:
                processed_image = validate_image_size(self.image)
                if processed_image and processed_image != self.image:
                    self.image = processed_image
            except Exception as e:
                print(f"Error processing image: {e}")
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return None


class Comment(models.Model):
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE, verbose_name="Related Post"
    )
    # Self-referencing field for creating nested comments ↓
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
    image = models.ImageField(
        upload_to='comment_images/',
        blank=True,
        null=True,
        validators=[validate_image_size],
        verbose_name="Attached Image"
    )
    file = models.FileField(
        upload_to='comment_files/',
        blank=True,
        null=True,
        validators=[validate_file_extension, validate_file_size],
        verbose_name="Attached File"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post} at {self.created_at}"

    # Check if a comment is a reply ↓
    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent is not None

    # Process the image before saving ↓
    def save(self, *args, **kwargs):
        if self.image:
            try:
                processed_image = validate_image_size(self.image)
                if processed_image != self.image:
                    self.image = processed_image
            except Exception as e:
                print(f"Error saving comment image: {e}")
                raise
        super().save(*args, **kwargs)
