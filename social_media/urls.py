from rest_framework import routers

from social_media.views import HashtagViewSet, PostViewSet, CommentViewSet


app_name = "social_media"

router = routers.DefaultRouter()

router.register("posts", PostViewSet)
router.register("comments", CommentViewSet)
router.register("hashtags", HashtagViewSet)


urlpatterns = router.urls
