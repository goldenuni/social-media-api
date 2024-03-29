from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from social_media.models import Hashtag, Post, Comment, Like
from social_media.permissions import IsAuthorOrReadOnly
from social_media.serializers import (
    HashtagSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    CommentListSerializer,
    CommentDetailSerializer,
    PostImageSerializer,
    CommentImageSerializer,
    LikeSerializer,
)


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class PostPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.prefetch_related(
        "author",
        "hashtags",
    )
    serializer_class = PostSerializer
    pagination_class = PostPagination
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )

    @staticmethod
    def _params_to_int(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostSerializer

    def get_queryset(self):
        queryset = self.queryset
        hashtags = self.request.query_params.get("hashtags")

        if hashtags:
            hashtags_id = self._params_to_int(hashtags)
            queryset = queryset.filter(hashtags__id__in=hashtags_id)

        return queryset.distinct()

    @action(
        detail=True,
        methods=["POST"],
        url_path="like",
        serializer_class=LikeSerializer,
    )
    def like(self, request, pk):
        """
        Endpoint for performing like action
        example: api/posts/pk/like/
        """
        post = get_object_or_404(
            Post,
            id=pk,
        )
        created_by = request.user
        serializer = LikeSerializer(data={"post": post.id, "created_by": created_by.id})
        serializer.is_valid(
            raise_exception=True,
        )
        serializer.save()
        response_serializer = PostDetailSerializer(post)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["POST"],
        url_path="unlike",
    )
    def unlike(self, request, pk):
        """
        Endpoint for performing unlike action
        example: api/posts/pk/unlike/
        """
        post = get_object_or_404(
            Post,
            id=pk,
        )
        created_by = request.user
        like = Like.objects.filter(
            post__id=post.id,
            created_by__id=created_by.id,
        )
        if not like:
            raise ValidationError("You have not liked this post yet")
        like.delete()
        response_serializer = PostDetailSerializer(post)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["POST"],
        url_path="upload_image",
        serializer_class=PostImageSerializer,
    )
    def upload_image(self, request, pk=None):
        """
        Endpoint for performing upload image action
        example: api/posts/pk/upload_image/
        """
        comment = self.get_object()
        serializer = self.get_serializer(comment, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related(
        "author",
        "post",
    )
    serializer_class = CommentSerializer
    pagination_class = PostPagination
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        if self.action == "retrieve":
            return CommentDetailSerializer
        return CommentSerializer

    @action(
        detail=True,
        methods=["POST"],
        url_path="upload_image",
        serializer_class=CommentImageSerializer,
    )
    def upload_image(self, request, pk=None):
        """
        Endpoint for performing upload image action
        example: api/comments/pk/upload_image/
        """
        comment = self.get_object()
        serializer = self.get_serializer(comment, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
