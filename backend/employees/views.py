import mimetypes
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrHR, IsEmployee
from audit.utils import log_action
from notifications.service import send_templated
from .models import Department, Employee, EmployeeDocument
from .serializers import (DepartmentSerializer, EmployeeDocumentSerializer, EmployeeSerializer, MyProfileSerializer)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrHR]
    pagination_class = None

    def perform_create(self, s):
        o = s.save(); log_action(self.request, "DEPARTMENT_CREATE", "Department", o.id, {"name": o.name})

    def perform_update(self, s):
        o = s.save(); log_action(self.request, "DEPARTMENT_UPDATE", "Department", o.id, {"name": o.name})

    def perform_destroy(self, o):
        if o.employees.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Department has employees; reassign them first.")
        log_action(self.request, "DEPARTMENT_DELETE", "Department", o.id, {"name": o.name}); o.delete()


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("user", "department")
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminOrHR]
    filterset_fields = ["department", "is_active", "designation"]
    search_fields = ["employee_code", "user__first_name", "user__last_name", "user__email", "designation"]
    ordering_fields = ["employee_code", "joining_date"]

    def perform_create(self, s):
        emp = s.save()
        log_action(self.request, "EMPLOYEE_CREATE", "Employee", emp.id, {"code": emp.employee_code})
        send_templated("EMPLOYEE_ONBOARDED", emp.user.email, {"name": emp.full_name, "username": emp.user.username, "password": emp._temp_password})
        self._temp = emp._temp_password

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        resp.data["temporary_password"] = self._temp  # shown once to HR (also emailed)
        return resp

    def perform_update(self, s):
        emp = s.save()
        log_action(self.request, "EMPLOYEE_UPDATE", "Employee", emp.id, {"fields": list(self.request.data.keys())})

    def destroy(self, request, *args, **kwargs):
        return Response({"error": "Employees are deactivated, not deleted. Use POST /deactivate/."}, status=405)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        emp = self.get_object()
        emp.is_active = False; emp.save(update_fields=["is_active"])
        emp.user.is_active = False; emp.user.save(update_fields=["is_active"])
        log_action(request, "EMPLOYEE_DEACTIVATE", "Employee", emp.id, {"code": emp.employee_code})
        return Response({"message": "Employee deactivated"})

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        emp = self.get_object()
        emp.is_active = True; emp.save(update_fields=["is_active"])
        emp.user.is_active = True; emp.user.save(update_fields=["is_active"])
        log_action(request, "EMPLOYEE_ACTIVATE", "Employee", emp.id, {"code": emp.employee_code})
        return Response({"message": "Employee activated"})

    @action(detail=True, methods=["get", "post"], parser_classes=[MultiPartParser, FormParser], url_path="documents")
    def documents(self, request, pk=None):
        emp = self.get_object()
        if request.method == "GET":
            return Response(EmployeeDocumentSerializer(emp.documents.all(), many=True).data)
        s = EmployeeDocumentSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        f = request.FILES["file"]
        doc = s.save(employee=emp, uploaded_by=request.user, original_name=f.name[:255])
        log_action(request, "DOCUMENT_UPLOAD", "EmployeeDocument", doc.id, {"employee": emp.employee_code, "title": doc.title})
        return Response(EmployeeDocumentSerializer(doc).data, status=status.HTTP_201_CREATED)


class DocumentDownloadView(APIView):
    """Authenticated download: HR/Admin any, an employee only their own documents."""
    def get(self, request, pk):
        doc = get_object_or_404(EmployeeDocument.objects.select_related("employee"), pk=pk)
        if not request.user.is_hr_or_admin and doc.employee.user_id != request.user.id:
            return Response({"error": "Not allowed"}, status=403)
        ctype = mimetypes.guess_type(doc.original_name)[0] or "application/octet-stream"
        return FileResponse(doc.file.open("rb"), as_attachment=True, filename=doc.original_name or "document", content_type=ctype)


class DocumentDeleteView(APIView):
    permission_classes = [IsAdminOrHR]

    def delete(self, request, pk):
        doc = get_object_or_404(EmployeeDocument, pk=pk)
        log_action(request, "DOCUMENT_DELETE", "EmployeeDocument", doc.id, {"title": doc.title})
        doc.file.delete(save=False); doc.delete()
        return Response(status=204)


class MyProfileView(APIView):
    permission_classes = [IsEmployee]

    def get(self, request):
        emp = request.user.employee
        data = MyProfileSerializer(emp).data
        data["documents"] = EmployeeDocumentSerializer(emp.documents.all(), many=True).data
        return Response(data)
