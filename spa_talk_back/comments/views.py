from rest_framework import viewsets, status, serializers, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, UserSerializer
from .utils import generate_captcha_text, generate_captcha_image


class LoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Генерация капчи для входа"""
        captcha_text = generate_captcha_text()
        captcha_image = generate_captcha_image(captcha_text)
        # Save in session
        request.session['login_captcha_text'] = captcha_text
        request.session.save()  # Force saving the session
        return Response({
            'captcha_image': captcha_image
        })

    def post(self, request):
        # Check captcha
        user_captcha = request.data.get('captcha', '').strip().upper()
        stored_captcha = request.session.get(
            'login_captcha_text', '').strip().upper()

        if not user_captcha or not stored_captcha:
            return Response(
                {"detail": "Captcha is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_captcha != stored_captcha:
            return Response(
                {"detail": "Invalid captcha"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Clear captcha from session
            del request.session['login_captcha_text']
            request.session.save()
        except KeyError:
            pass

        # Authenticate user
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            })
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)


class RegisterUserView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def get(self, request):
        """Генерация капчи для регистрации"""
        captcha_text = generate_captcha_text()
        captcha_image = generate_captcha_image(captcha_text)

        # Save in session
        request.session['register_captcha_text'] = captcha_text
        request.session.save()  # Force saving the session

        return Response({
            'captcha_image': captcha_image
        })

    def post(self, request):
        try:
            # Check captcha
            user_captcha = request.data.get('captcha', '').strip().upper()
            stored_captcha = request.session.get(
                'register_captcha_text', '').strip().upper()

            if not user_captcha or not stored_captcha:
                return Response(
                    {"detail": "Captcha is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user_captcha != stored_captcha:
                return Response(
                    {"detail": "Invalid captcha"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Clear captcha from session
            del request.session['register_captcha_text']

            user_data = {
                'username': request.data.get('username'),
                'email': request.data.get('email'),
                'password': request.data.get('password'),
                'profile': {}
            }

            # Photo processing
            if 'profile.photo' in request.FILES:
                user_data['profile']['photo'] = request.FILES['profile.photo']

            # Processing homepage
            home_page = request.data.get('profile.home_page')
            if home_page:
                user_data['profile']['home_page'] = home_page

            print("Processed data:", user_data)

            serializer = UserSerializer(
                data=user_data, context={'request': request})
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    "detail": "User registered successfully!",
                    "username": user.username
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Registration error:", str(e))
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Post.objects.all()
        username = self.request.query_params.get('username', None)
        email = self.request.query_params.get('email', None)
        date_order = self.request.query_params.get('date_order', None)

        if username:
            queryset = queryset.filter(user__username__icontains=username)
        if email:
            queryset = queryset.filter(user__email__icontains=email)
        if date_order:
            order = '-created_at' if date_order == 'desc' else 'created_at'
            queryset = queryset.order_by(order)

        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        parent_id = self.request.data.get('parent')
        parent_comment = None
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id)
            except Comment.DoesNotExist:
                raise serializers.ValidationError(
                    {"parent": "Parent comment does not exist."})
        serializer.save(user=self.request.user, parent=parent_comment)


class PostCommentsView(APIView):
    def get(self, request, post_id):
        comments = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer(
            comments, many=True, context={'request': request})
        return Response(serializer.data)
