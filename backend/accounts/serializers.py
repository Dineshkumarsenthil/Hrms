from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    has_employee = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "is_active", "must_change_password", "last_login", "has_employee"]
        read_only_fields = ["id", "username", "email", "last_login", "has_employee"]

    def get_has_employee(self, obj):
        return hasattr(obj, "employee")


class LoginSerializer(TokenObtainPairSerializer):
    """Accepts username OR email; embeds role in the token and returns the user."""

    def validate(self, attrs):
        ident = attrs.get("username", "")
        if "@" in ident:
            u = User.objects.filter(email__iexact=ident).first()
            if u:
                attrs["username"] = u.username
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        return token


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, v):
        if not self.context["request"].user.check_password(v):
            raise serializers.ValidationError("Old password is incorrect.")
        return v

    def validate_new_password(self, v):
        validate_password(v, self.context["request"].user)
        return v
