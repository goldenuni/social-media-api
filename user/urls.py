from rest_framework import routers

from user.views import UserViewSet

app_name = "user"

router = routers.DefaultRouter()
router.register("", UserViewSet)

urlpatterns = router.urls
