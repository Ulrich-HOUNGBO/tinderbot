from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {"password": {"write_only": True}}
        fields = [
            "id",
            "username",
            "password",
            "email",
            "is_active",
            "is_superuser"
        ]
        permissions_classes = [
            "rest_framework.permissions.AllowAny",
        ]

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data["email"],
        )

        user.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise serializers.ValidationError(
                "New password and confirm password do not match."
            )

        return data


class LoginSerializer(serializers.Serializer):

    class Meta:
        fields = ["email", "password"]
        permissions_classes = [
            "rest_framework.permissions.AllowAny",
        ]

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=False, style={"input_type": "password"})

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token["is_active"] = user.is_active
        return token

    def validate(self, attrs):
        password = attrs.get("password")
        email = attrs.get("email")
        self.user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not self.user:
            self.user = User.objects.filter(email=email).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user and self.user.is_active:
            data = super().validate(attrs)
            refresh = self.get_token(self.user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)
            return data


class SendMailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserPasswordResetSerializer(serializers.Serializer):
    newPassword = serializers.CharField(max_length=255, style={"input_type": "password"})
    confirmPassword = serializers.CharField(max_length=255, style={"input_type": "password"})

    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        try:
            print("hello")
            newPassword = attrs.get("newPassword")
            confirmPassword = attrs.get("confirmPassword")
            uid = self.context.get("uid")
            token = self.context.get("token")
            print(uid, token)
            if newPassword != confirmPassword:
                raise serializers.ValidationError("Mots de passe non identiques")
            _id = smart_str(urlsafe_base64_decode(uid))
            if not User.objects.filter(id=_id).exists():
                raise serializers.ValidationError("Utilisateur non trouvé")
            user = User.objects.get(id=_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not Valid or Expired")
            user.set_password(newPassword)
            user.save()
            return attrs

        except DjangoUnicodeDecodeError as e:
            print(f"DjangoUnicodeDecodeError occurred: {e}")
            raise serializers.ValidationError("Token is not Valid or Expired")
