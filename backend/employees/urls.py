from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, DocumentDeleteView, DocumentDownloadView, EmployeeViewSet, MyProfileView

router = DefaultRouter()
router.register("departments", DepartmentViewSet, basename="departments")
router.register("", EmployeeViewSet, basename="employees")

urlpatterns = [
    path("me/", MyProfileView.as_view()),
    path("documents/<int:pk>/download/", DocumentDownloadView.as_view()),
    path("documents/<int:pk>/", DocumentDeleteView.as_view()),
] + router.urls
