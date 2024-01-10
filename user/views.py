from django.db.models import Count
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import Follow
from user.permissions import IsOwnerOrReadOnly
from user.serializers import (
    UserSerializer,
    UserListSerializer,
    UserDetailSerializer,
)


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
            "GET",
        ],
    )
    def follow(self, request, pk=None):
        """
        Endpoint for performing follow action
        example: api/users/pk/follow/
        """
        user = request.user
        user_follow = self.get_object()
        Follow.objects.create(follower=user, following=user_follow)
        serializer = self.get_serializer_class()(user_follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=[
            "GET",
        ],
    )
    def unfollow(self, request, pk=None):
        """
        Endpoint for performing unfollow action
        example: api/users/pk/unfollow/
        """

        user = request.user
        user_follow = self.get_object()
        follow_conn = Follow.objects.filter(
            follower=user, following=user_follow
        ).first()
        follow_conn.delete()
        serializer = self.get_serializer_class()(user_follow)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["GET", "PUT", "PATCH", "DELETE"],
    )
    def me(self, request):
        """Endpoint for managing user profile"""
        user = request.user

        if request.method == "GET":
            serializer = self.get_serializer_class()(user)
            return Response(serializer.data)

        elif request.method in ["PUT", "PATCH", "DELETE"]:
            self.check_object_permissions(request, user)
            if request.method == "DELETE":
                user.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                serializer = self.get_serializer_class()(
                    user, data=request.data, partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)

    @action(
        detail=False,
        methods=["POST"],
    )
    def register(self, request):
        """Endpoint for creating a profile"""
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        description="Endpoint to invalidate a refresh token and log the user out.",
        request={"refresh_token": "string"},
        responses={
            205: None,
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
