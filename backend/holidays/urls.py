from rest_framework.routers import DefaultRouter
from .views import HolidayViewSet

router = DefaultRouter()
router.register("", HolidayViewSet, basename="holidays")
urlpatterns = router.urls
