from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from audit.utils import log_action
from .permissions import IsAdmin, ROLE_MATRIX
from .serializers import ChangePasswordSerializer, LoginSerializer, UserSerializer

User = get_user_model()


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if resp.status_code == 200:
            u = User.objects.get(username=resp.data["user"]["username"])
            log_action(request, "LOGIN", "User", u.id, user=u)
        return resp


class LogoutView(APIView):
    def post(self, request):
        try:
            RefreshToken(request.data.get("refresh")).blacklist()
        except TokenError:
            return Response({"error": "Invalid refresh token"}, status=400)
        log_action(request, "LOGOUT", "User", request.user.id)
        return Response({"message": "Logged out"})


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    def post(self, request):
        s = ChangePasswordSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        request.user.set_password(s.validated_data["new_password"])
        request.user.must_change_password = False
        request.user.save()
        log_action(request, "PASSWORD_CHANGE", "User", request.user.id)
        return Response({"message": "Password updated"})


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """Admin: role & permission management (change role, activate/deactivate)."""
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "email"]
    http_method_names = ["get", "patch", "head", "options"]

    def perform_update(self, serializer):
        if serializer.instance.id == self.request.user.id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You cannot change your own role/status.")
        old = {"role": serializer.instance.role, "is_active": serializer.instance.is_active}
        obj = serializer.save()
        log_action(self.request, "USER_UPDATE", "User", obj.id, {"old": old, "new": {"role": obj.role, "is_active": obj.is_active}})


class RoleMatrixView(APIView):
    def get(self, request):
        return Response(ROLE_MATRIX)
