from django.urls import path
from .views import CommentListCreateView, ReplyListCreateView

urlpatterns = [
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('replies/', ReplyListCreateView.as_view(), name='reply-list-create'),
]
