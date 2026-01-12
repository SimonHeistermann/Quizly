from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirmed_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "username": {"required": True},
        }

    def validate(self, attrs):
        password = attrs.get("password")
        confirmed_password = attrs.get("confirmed_password")
        email = attrs.get("email")

        if password != confirmed_password:
            raise serializers.ValidationError({"confirmed_password": "Passwords do not match."})

        validate_password(password)

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({"email": "Email already exists."})

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirmed_password", None)
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
