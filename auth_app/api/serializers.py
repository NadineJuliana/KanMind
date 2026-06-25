from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer used for validating and creating new user accounts.
    """

    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        """
        Ensures that the email address is unique.
        """

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def validate(self, attrs):
        """
        Ensures that both password fields match.
        """

        password = attrs["password"]
        repeated_password = attrs["repeated_password"]
        if password != repeated_password:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """
        Creates and returns a new user with the validated registration data.
        """

        fullname = validated_data["fullname"]
        email = validated_data["email"]
        password = validated_data["password"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=fullname,
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer used for validating login credentials.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for authentication response user data.
    """

    fullname = serializers.CharField(source="first_name", read_only=True)
    user_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "user_id"]


class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for nested user data in boards, tasks and comments.
    """

    fullname = serializers.CharField(source="first_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
