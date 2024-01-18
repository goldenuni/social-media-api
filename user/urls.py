from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.views import UserViewSet, LogoutView

app_name = "user"

router = routers.DefaultRouter()
router.register("", UserViewSet)

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/logout/", LogoutView.as_view(), name="auth_logout"),
    path("", include(router.ursl)),
]
