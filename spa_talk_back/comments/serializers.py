from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Post, Comment


class ProfileSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['photo', 'photo_url', 'home_page']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo:
            return request.build_absolute_uri(obj.photo.url)
        return request.build_absolute_uri('/media/user_photos/default.jpg')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        try:
            profile_data = validated_data.pop('profile', {})
            
            # Create a new user
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password']
            )

            # Update the user profile
            if profile_data:
                profile = user.profile # Get the user profile
                if 'photo' in profile_data:
                    profile.photo = profile_data['photo']
                if 'home_page' in profile_data:
                    profile.home_page = profile_data['home_page']
                profile.save()

            return user
        except Exception as e:
            print("Error in create:", str(e))
            raise

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'text', 'user', 'image', 'image_url', 'file', 'created_at', 'updated_at', 'comments_count']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def get_comments_count(self, obj):
        return Comment.objects.filter(post=obj).count()  

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    parent_text = serializers.SerializerMethodField()
    parent_info = serializers.SerializerMethodField()  

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'text', 'created_at', 'updated_at', 
                 'image', 'file', 'parent', 'replies', 'level', 'parent_text',
                 'parent_info']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            serializer = CommentSerializer(obj.replies.all(), many=True, context=self.context)
            return serializer.data
        return []

    def get_level(self, obj):
        level = 0
        parent = obj.parent
        while parent is not None:
            level += 1
            parent = parent.parent
        return level

    def get_parent_text(self, obj):
        if obj.parent:
            return obj.parent.text
        return None

    def get_parent_info(self, obj):
        if obj.parent:
            return {
                'id': obj.parent.id,
                'text': obj.parent.text,
                'username': obj.parent.user.username
            }
        return None

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
