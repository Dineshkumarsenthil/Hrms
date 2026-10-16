from rest_framework.routers import DefaultRouter
from .views import BroadcastViewSet, EmailLogViewSet, EmailTemplateViewSet, NotificationViewSet

router = DefaultRouter()
router.register("logs", EmailLogViewSet, basename="email-logs")
router.register("templates", EmailTemplateViewSet, basename="email-templates")
router.register("broadcasts", BroadcastViewSet, basename="broadcasts")
router.register("", NotificationViewSet, basename="notifications")
urlpatterns = router.urls
