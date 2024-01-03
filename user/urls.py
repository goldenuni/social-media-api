from django.urls import path, include
from rest_framework import routers

from user.views import ManageUserView, UserViewSet

app_name = "user"

router = routers.DefaultRouter()
router.register("", UserViewSet)

urlpatterns = [
    path("me/", ManageUserView.as_view(), name="manage-user"),
    path("", include(router.urls), name="user"),
]
