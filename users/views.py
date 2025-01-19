from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_bytes
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from mail.reset_password_mail import send_mail_template
from tinderbot import settings
from users.models import User
from users.serializers import UserSerializer, LoginSerializer, ChangePasswordSerializer, SendMailSerializer, \
    UserPasswordResetSerializer


# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @extend_schema(methods=["post"], request=LoginSerializer, responses=UserSerializer)
    @action(
        detail=False,
        methods=["post"],
        url_path="register",
        permission_classes=[permissions.AllowAny],
    )
    def register(self, request, *args, **kwargs):
        try:
            serializer = UserSerializer(data=self.request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        methods=["post"],
        request=LoginSerializer,
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Invalid credentials."),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="login",
        serializer_class=LoginSerializer,
        permission_classes=[permissions.AllowAny],
    )
    def login(self, request):
        try:
            email = self.request.data.get("email")
            password = self.request.data.get("password")
            user = authenticate(request, email=email, password=password)

            if user is not None:
                user_model = User.objects.get(email=email)
                if user_model.is_active:
                    print(user_model.is_active)
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {
                            "access": str(refresh.access_token),
                            "refresh": str(refresh),
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"detail": "User account is inactive."},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            else:
                return Response(
                    {"detail": "Invalid credentials."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        methods=["get"],
        responses=UserSerializer,
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        try:
            queryset = User.objects.get(id=request.user.id)
            serializer = UserSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        methods=["post"],
        request=ChangePasswordSerializer,
        responses=UserSerializer,
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="changePassword",
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=ChangePasswordSerializer,
    )
    def change_password(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.user.id)
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response(
                    {"detail": "Mot de passe incorrect."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(serializer.data.get("new_password"))
            user.save()

            return Response(
                {
                    "status": "success",
                    "code": status.HTTP_200_OK,
                    "message": "Password updated successfully",
                }
            )

        return Response(
            {
                "detail": "You cannot change the password, your password's do not match",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=["patch"],
        url_path="allow-user-access/<uuid:user_id>",
        permission_classes=[permissions.IsAdminUser],
    )
    def allow_user_access(self, request, *args, **kwargs):
        try:
            user_id = self.kwargs.get("user_id")
            user = User.objects.get(id=user_id)
            if not user.is_active:
                user.is_active = True
                user.save()
                return Response(
                    {"message": "Access allow to user successfully"},
                    status=status.HTTP_200_OK,
                )
            user.is_active = False

            user.save()
            return Response(
                {"message": "You have successfully denied access to the user"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        methods=["get"],
        url_path="get-all-users",
        permission_classes=[permissions.IsAdminUser],
    )
    def get_all_users(self, request):
        try:
            queryset = User.objects.all()
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"], url_path="send-mail-reset-password")
    def reset_password_send_mail(self, request):
        serializer = SendMailSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data.get("email")

            print(email)
            try:
                user = User.objects.get(email=email)
                print(user.email)
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = f"{settings.FRONTEND_URL}/login/reset-password?uid={uid}&token={token}"
                print(reset_url)
                send_mail_template(
                    user.email,
                    "Reset password!",
                    'reset_password_email.html',
                    {"name": user.username, "reset_url": reset_url},
                )

                return Response(
                    {
                        "message": "You will receive an email with instructions to reset your password"
                    },
                    status=status.HTTP_200_OK,
                )
            except ObjectDoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["patch"],
        url_path="reset-password", )

    def reset_password(self, request, format=None):
        serializers = UserPasswordResetSerializer(data=request.data)

        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("newPassword")

        if uid is None or token is None or new_password is None:
            return Response(
                {"error": "UID, token, and new password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"error": "Invalid token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()

            return Response(
                {"message": "Password reset successfully"},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid UID."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
