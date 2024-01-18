from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import Follow


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "nickname",
            "first_name",
            "last_name",
            "avatar",
            "biography",
            "city",
            "is_staff",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserListSerializer(UserSerializer):
    num_following = serializers.IntegerField(read_only=True)
    num_followers = serializers.IntegerField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "nickname",
            "first_name",
            "last_name",
            "avatar",
            "biography",
            "city",
            "is_staff",
            "num_following",
            "num_followers",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5}}


class UserDetailSerializer(UserSerializer):
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "nickname",
            "first_name",
            "last_name",
            "avatar",
            "biography",
            "city",
            "is_staff",
            "following",
            "followers",
        )

    @staticmethod
    def get_following(obj):
        return FollowSerializer(
            obj.following.all(),
            many=True,
        ).data

    @staticmethod
    def get_followers(obj):
        return UserFollowersSerializer(
            obj.followers.all(),
            many=True,
        ).data


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source="user_following.id")
    nickname = serializers.ReadOnlyField(
        source="user.nickname",
    )

    class Meta:
        model = Follow
        fields = (
            "id",
            "nickname",
        )


class UserFollowersSerializer(serializers.ModelSerializer):
    nickname = serializers.ReadOnlyField(
        source="follower.nickname",
    )

    class Meta:
        model = Follow
        fields = (
            "follower",
            "nickname",
        )
