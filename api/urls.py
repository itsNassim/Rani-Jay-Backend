from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegisterView, MeView, ComplaintViewSet

router = DefaultRouter()
router.register(r"complaints", ComplaintViewSet, basename="complaint")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
