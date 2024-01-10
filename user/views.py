from django.db.models import Count
from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from user.models import Follow
from user.permissions import IsOwnerOrReadOnly
from user.serializers import (
    UserSerializer,
    UserListSerializer,
    UserDetailSerializer,
)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        nickname = self.request.query_params.get("nickname")
        city = self.request.query_params.get("city")

        if nickname:
            queryset = queryset.filter(user__nickname=nickname)
        if city:
            queryset = queryset.filter(user__city=city)

        if self.action == "list":
            queryset = queryset.annotate(
                num_following=Count("following"),
                num_followers=Count("followers"),
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer

        if self.action in ["retrieve", "follow", "unfollow"]:
            return UserDetailSerializer

        return UserSerializer

    @action(
        detail=True,
        methods=[
            "POST",
        ],
    )
    def follow(self, request, pk=None):
        """ "Follow the user. ex: users/<pk>/follow/"""
        user = request.user
        user_follow = self.get_object()
        Follow.objects.create(follower=user, following=user_follow)
        serializer = self.get_serializer_class()(user_follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=[
            "DELETE",
        ],
    )
    def unfollow(self, request, pk=None):
        """Unfollow the user. ex. users/<pk>/unfollow/"""
        user = request.user
        user_follow = self.get_object()
        follow_conn = Follow.objects.filter(
            follower=user, following=user_follow
        ).first()
        follow_conn.delete()
        serializer = self.get_serializer_class()(user_follow)
        return Response(serializer.data, status.HTTP_200_OK)
