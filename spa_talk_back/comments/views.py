from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MainComment, Reply
from .serializers import CommentSerializer, ReplySerializer
from django.core.paginator import Paginator


class CommentListCreateView(APIView):
    def get(self, request):
        comments = MainComment.objects.all().order_by('-created_at')
        paginator = Paginator(comments, 25)
        page_number = request.query_params.get('page')
        page_obj = paginator.get_page(page_number)
        serializer = CommentSerializer(page_obj, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReplyListCreateView(APIView):
    def get(self, request):
        replies = Reply.objects.all()
        serializer = ReplySerializer(replies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
