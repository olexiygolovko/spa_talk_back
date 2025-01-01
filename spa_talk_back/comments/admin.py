from django.contrib import admin
from .models import Post, Comment, Profile


# Register the objects we need in the admin panel
admin.site.register(Comment)
admin.site.register(Post)
admin.site.register(Profile)
