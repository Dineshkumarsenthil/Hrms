from rest_framework.routers import DefaultRouter
from .views import MonthlyVariablePayViewSet, PayrollViewSet, SalaryComponentViewSet, SalaryStructureViewSet

router = DefaultRouter()
router.register("components", SalaryComponentViewSet, basename="salary-components")
router.register("structures", SalaryStructureViewSet, basename="salary-structures")
router.register("variable-pay", MonthlyVariablePayViewSet, basename="variable-pay")
router.register("", PayrollViewSet, basename="payroll")
urlpatterns = router.urls
