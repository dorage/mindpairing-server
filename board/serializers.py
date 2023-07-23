
from config import settings
from membership.serializers import UserSimpleProfileSerializer
from .models import *
from hashtag.serializer import *


class BoardHashtagSerializer(serializers.ModelSerializer):
    topic = serializers.SerializerMethodField('get_topic', read_only=True)

    def get_topic(self, obj):
        return obj.hashtag_id.text

    class Meta:
        model = BoardHashtagAssoc
        fields = ('index', 'topic')


class BoardSerializer(serializers.ModelSerializer):
    topics = serializers.SerializerMethodField('get_topics')

    def get_topics(self, obj: Board):
        serializer = BoardHashtagSerializer(obj.hashtag_assoc_set, many=True)
        return serializer.data
    class Meta:
        model = Board
        fields = ('index', 'category', 'topics')


class SimplePostSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField(read_only=True)
    topic = serializers.CharField(source='hashtag_id.text', read_only=True)
    author = UserSimpleProfileSerializer(source='user_id', read_only=True)
    is_liked = serializers.BooleanField(read_only=True)
    comment_count = serializers.SerializerMethodField(read_only=True)

    short_content = serializers.SerializerMethodField(read_only=True)
    create_at = serializers.DateTimeField(format=settings.DATETIME_FORMAT)
    update_at = serializers.DateTimeField(format=settings.DATETIME_FORMAT)

    def __init__(self, *args, **kwargs):
        self.user_id_value = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)

    def to_representation(self, instance: Post):
        data = super().to_representation(instance)

        try:
            instance.like_post_assoc_set.get(user_id=self.user_id_value)
            data['is_liked'] = True
        except Exception as e:
            data['is_liked'] = False

        return data

    def get_category(self, obj: Post):
        return obj.board_id.category

    def get_comment_count(self, obj: Post):
        return obj.comment_set.count()

    def get_short_content(self, obj):
        return obj.content[:50]

    class Meta:
        model = Post
        fields = ('id', 'category', 'topic', 'mbti', 'author', 'title', 'short_content', 'view', 'like', 'is_liked', 'comment_count', 'report', 'create_at', 'update_at')


class PostWithImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField(source='id', read_only=True)
    author = UserSimpleProfileSerializer(source='user_id', read_only=True)
    is_liked = serializers.BooleanField(read_only=True)
    create_at = serializers.DateTimeField(format=settings.DATETIME_FORMAT)
    delete_at = serializers.DateTimeField(format=settings.DATETIME_FORMAT)

    def __init__(self, *args, **kwargs):
        self.user_id_value = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)

    def to_representation(self, instance: Comment):
        data = super().to_representation(instance)

        try:
            instance.like_comment_assoc_set.get(user_id=self.user_id_value)
            data['is_liked'] = True
        except Exception as e:
            data['is_liked'] = False

        return data


    class Meta:
        model = Comment
        fields = ('comment_id', 'content', 'like', 'is_liked', 'report', 'create_at', 'delete_at', 'author', 'parent_comment_id')


class PostDetailSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField(source='id', read_only=True)
    create_at = serializers.DateTimeField(format=settings.DATETIME_FORMAT)
    update_at = serializers.DateTimeField(format=settings.DATETIME_FORMAT)
    category = serializers.CharField(source='board_id.category')
    topic = serializers.CharField(source='hashtag_id.text')
    author = UserSimpleProfileSerializer(source='user_id', read_only=True)
    is_liked = serializers.BooleanField(read_only=True)
    create_at = serializers.DateTimeField(format=settings.DATETIME_FORMAT)
    update_at = serializers.DateTimeField(format=settings.DATETIME_FORMAT)

    def __init__(self, *args, **kwargs):
        self.user_id_value = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)

    def to_representation(self, instance: Post):
        data = super().to_representation(instance)

        try:
            instance.like_post_assoc_set.get(user_id=self.user_id_value)
            data['is_liked'] = True
        except Exception as e:
            data['is_liked'] = False

        return data

    def update(self, instance, validated_data):
        title = validated_data.get('title', instance.title)
        content = validated_data.get('content', instance.content)
        instance.save()

    class Meta:
        model = Post
        fields = ('post_id', 'category', 'topic', 'mbti', 'author', 'title', 'content', 'view', 'like', 'is_liked', 'create_at', 'update_at')


class LikePostAssocSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikePostAssoc
        fields = '__all__'


class LikeCommentAssocSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikePostAssoc
        fields = '__all__'
