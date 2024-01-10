from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user.models import Follow
from user.serializers import UserSerializer


def detail_url(user_id):
    return reverse("user:user-detail", args=[user_id])


class UserViewSetTest(TestCase):
    REGISTER_URL = reverse("user:user-register")

    def setUp(self):
        self.client = APIClient()

    def test_follow_user(self):
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword",
            nickname="testuser",
        )
        user_to_follow = get_user_model().objects.create_user(
            email="follow@example.com",
            password="followpassword",
            nickname="followuser",
        )

        self.client.force_authenticate(user=user)
        url = detail_url(user_to_follow.id)
        response = self.client.get(url + "follow/")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Follow.objects.filter(follower=user, following=user_to_follow).exists()
        )

    def test_unfollow_user(self):
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword",
            nickname="testuser",
        )
        user_to_unfollow = get_user_model().objects.create_user(
            email="unfollow@example.com",
            password="unfollowpassword",
            nickname="unfollowuser",
        )

        follow_conn = Follow.objects.create(follower=user, following=user_to_unfollow)

        self.client.force_authenticate(user=user)
        url = detail_url(user_to_unfollow.id)
        response = self.client.get(url + "unfollow/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Follow.objects.filter(follower=user, following=user_to_unfollow).exists()
        )

    def test_me_get_profile(self):
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword",
            nickname="testuser",
        )

        self.client.force_authenticate(user=user)
        url = reverse("user:user-me")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], user.email)

    def test_me_update_profile(self):
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword",
            nickname="testuser",
        )

        self.client.force_authenticate(user=user)
        url = reverse("user:user-me")
        new_data = {
            "nickname": "updatednickname",
            "biography": "Updated biography",
        }
        response = self.client.patch(url, new_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], new_data["nickname"])
        self.assertEqual(response.data["biography"], new_data["biography"])

    def test_me_delete_profile(self):
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword",
            nickname="testuser",
        )

        self.client.force_authenticate(user=user)
        url = reverse("user:user-me")
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(get_user_model().objects.filter(id=user.id).exists())

    def test_user_registration(self):
        payload = {
            "email": "test@example.com",
            "password": "testpassword",
            "nickname": "testuser",
            "first_name": "Test",
            "last_name": "User",
        }

        response = self.client.post(self.REGISTER_URL, payload)
        user = get_user_model().objects.get(email=payload["email"])
        serializer = UserSerializer(user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)
        self.assertTrue(user.check_password(payload["password"]))
