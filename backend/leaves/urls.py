from rest_framework.routers import DefaultRouter
from .views import LeaveBalanceViewSet, LeaveRequestViewSet, LeaveTypeViewSet

router = DefaultRouter()
router.register("types", LeaveTypeViewSet, basename="leave-types")
router.register("balances", LeaveBalanceViewSet, basename="leave-balances")
router.register("requests", LeaveRequestViewSet, basename="leave-requests")
urlpatterns = router.urls
