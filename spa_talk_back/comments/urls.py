from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import PostViewSet, CommentViewSet, RegisterUserView, PostCommentsView, LoginView

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('posts/<int:post_id>/comments/',
         PostCommentsView.as_view(), name='post-comments'),
]

urlpatterns += router.urls
