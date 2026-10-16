from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MyShiftView, ShiftAssignmentViewSet, ShiftViewSet

router = DefaultRouter()
router.register("assignments", ShiftAssignmentViewSet, basename="shift-assignments")
router.register("", ShiftViewSet, basename="shifts")

urlpatterns = [path("my-shift/", MyShiftView.as_view())] + router.urls
