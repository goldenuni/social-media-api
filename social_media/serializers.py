from rest_framework import serializers

from social_media.models import Post, Like, Comment, Hashtag


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = (
            "id",
            "created_by",
            "post",
        )

    def validate(self, data):
        like = Like.objects.filter(
            post_id=data["post"], created_by_id=data["created_by"]
        )
        if like:
            raise serializers.ValidationError("You have already liked this post")
        return data


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = (
            "id",
            "name",
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "created_at",
            "post",
            "content",
            "image",
        )


class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="nickname",
    )
    post = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="title",
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "created_at",
            "post",
            "content",
            "image",
        )


class CommentPostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="nickname",
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "created_at",
            "author",
            "title",
            "content",
            "image",
        )


class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="nickname",
    )
    post = CommentPostSerializer(
        many=False,
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "created_at",
            "post",
            "content",
            "image",
        )


class CommentImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=False)

    class Meta:
        model = Comment
        fields = (
            "id",
            "image",
        )


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "created_at",
            "title",
            "content",
            "image",
            "hashtags",
        )


class PostListSerializer(serializers.ModelSerializer):
    hashtags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="nickname",
    )
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    @staticmethod
    def get_comments_count(obj):
        return obj.comments.count()

    @staticmethod
    def get_likes_count(obj):
        return obj.likes.count()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "created_at",
            "title",
            "image",
            "hashtags",
            "comments_count",
            "likes_count",
        )


class PostCommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="nickname",
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "created_at",
            "content",
        )


class PostLikeSerializer(LikeSerializer):
    created_by = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="nickname",
    )

    class Meta:
        model = Like
        fields = (
            "id",
            "created_by",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(
        many=True,
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="nickname",
    )
    likes = PostLikeSerializer(
        many=True,
        read_only=True,
    )
    comments = PostCommentSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "created_at",
            "title",
            "content",
            "image",
            "hashtags",
            "comments",
            "likes",
        )


class PostImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=False)

    class Meta:
        model = Post
        fields = (
            "id",
            "image",
        )
