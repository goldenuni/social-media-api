from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from social_media.models import Post, Hashtag
from social_media.serializers import (
    PostListSerializer, PostDetailSerializer,
)

POST_URL = reverse("social-media:post-list")


def detail_url(post_id: int):
    return reverse("social-media:post-detail", args=[post_id])


def sample_hashtag(**params):
    defaults = {
        "name": "Test Hashtag",
    }
    defaults.update(params)
    return Hashtag.objects.create(**defaults)


def sample_post(author, **params):
    defaults = {
        "title": "Test Post",
        "content": "This is a test post.",
    }
    defaults.update(params)
    return Post.objects.create(author=author, **defaults)


class AuthenticatedPostApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_posts(self):
        sample_post(self.user)
        post_with_hashtags = sample_post(self.user, title="Post with Hashtags")

        hashtag1 = sample_hashtag(name="test")
        hashtag2 = sample_hashtag(name="django")

        post_with_hashtags.hashtags.add(hashtag1, hashtag2)

        res = self.client.get(POST_URL)

        posts = Post.objects.all()
        serializer = PostListSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_filter_posts_by_hashtag(self):
        post1 = sample_post(self.user, title="Test post")
        post2 = sample_post(self.user, title="Another test post")

        hashtag1 = sample_hashtag(name="test")
        hashtag2 = sample_hashtag(name="django")

        post1.hashtags.add(hashtag1)
        post2.hashtags.add(hashtag2)

        post3 = sample_post(self.user, title="Another test post 1")

        res = self.client.get(
            POST_URL, {"hashtags": f"{hashtag1.id}, {hashtag2.id}"}
        )

        serializer1 = PostListSerializer(post1)
        serializer2 = PostListSerializer(post2)
        serializer3 = PostListSerializer(post3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_retrieve_post_detail(self):
        post = sample_post(self.user)
        post.hashtags.add(sample_hashtag(name="test"))

        url = detail_url(post.id)
        res = self.client.get(url)

        serializer = PostDetailSerializer(post)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_post(self):
        payload = {
            "title": "Test Post",
            "content": "This is a test post.",
        }

        res = self.client.post(POST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_post_with_hashtags(self):
        hashtag1 = sample_hashtag(name="test")
        hashtag2 = sample_hashtag(name="django")

        payload = {
            "title": "Test Post",
            "content": "This is a test post.",
            "hashtags": [hashtag1.id, hashtag2.id],
        }

        res = self.client.post(POST_URL, payload)
        post = Post.objects.get(id=res.data["id"])
        hashtags = post.hashtags.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(hashtags.count(), 2)
        self.assertIn(hashtag1, hashtags)
        self.assertIn(hashtag2, hashtags)

    def test_update_post(self):
        post = sample_post(self.user)
        payload = {
            "title": "Updated Post",
        }
        url = detail_url(post.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_post(self):
        post = sample_post(self.user)
        url = detail_url(post.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
