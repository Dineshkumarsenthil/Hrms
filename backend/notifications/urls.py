from rest_framework.routers import DefaultRouter
from .views import EmailLogViewSet, EmailTemplateViewSet

router = DefaultRouter()
router.register("logs", EmailLogViewSet, basename="email-logs")
router.register("templates", EmailTemplateViewSet, basename="email-templates")
urlpatterns = router.urls
