from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    """Uniform error shape: {"error": "...", "details": {...}}"""
    if isinstance(exc, DjangoValidationError):
        return Response({"error": "Validation failed", "details": exc.messages}, status=400)
    response = exception_handler(exc, context)
    if response is None:
        return None
    data = response.data
    if isinstance(data, dict) and "detail" in data and len(data) == 1:
        response.data = {"error": str(data["detail"])}
    else:
        response.data = {"error": "Validation failed" if response.status_code == 400 else "Request failed", "details": data}
    return response
