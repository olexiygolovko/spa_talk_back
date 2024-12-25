from rest_framework import serializers
from .models import MainComment, Reply


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainComment
        fields = '__all__'


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = '__all__'
