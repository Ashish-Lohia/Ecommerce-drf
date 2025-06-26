from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(
        write_only=True, required=True, min_length=8, label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["id", "fullname", "email", "password", "password2"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"Warning: Password don't match"})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if user and user.is_active:
            data["user"] = user
            return data
        raise serializers.ValidationError("Invalid Credentials")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class OtherUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["fullname", "role", "profilePic"]


class AllUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class EditUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "fullname", "profilePic", "phoneNo"]

    def validate_email(self, value):
        user = self.context["request"].user
        if User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already in use by another user."
            )
        return value
