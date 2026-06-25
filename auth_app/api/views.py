from django.contrib.auth import authenticate, get_user_model

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserResponseSerializer,
)

User = get_user_model()


class RegistrationView(GenericAPIView):
    """
    Creates a new user account and returns an authentication token.
    """

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserResponseSerializer(user).data
        user_data["token"] = token.key

        return Response(user_data, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    """
    Authenticates a user and returns an authentication token.
    """
    
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user_object = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=user_object.username, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserResponseSerializer(user).data
        user_data["token"] = token.key

        return Response(user_data, status=status.HTTP_200_OK)
