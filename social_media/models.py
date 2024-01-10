from django.contrib.auth import get_user_model
from django.db import models

from path_creator import image_file_path


class Hashtag(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return "#" + self.name


class Post(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        null=True,
        related_name="posts",
        on_delete=models.CASCADE,
    )
    created_at = models.DateField(
        auto_now_add=True,
    )
    title = models.CharField(
        max_length=64,
    )
    content = models.TextField()
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=image_file_path,
    )
    hashtags = models.ManyToManyField(Hashtag, related_name="posts", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        get_user_model(),
        null=True,
        on_delete=models.CASCADE,
    )
    created_at = models.DateField(
        auto_now_add=True,
    )
    content = models.TextField()
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=image_file_path,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.nickname} commented {self.post}"


class Like(models.Model):
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    def __str__(self):
        return f"{self.created_by.nickname} liked {self.post}"
