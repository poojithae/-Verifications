from datetime import datetime, timedelta
from django.utils import timezone
import random
from django.conf import settings
from rest_framework import serializers
from .utils import send_otp
from .models import *



class UserSerializer(serializers.ModelSerializer):
    """
    User Serializer.

    Used in POST and GET
    """

    password1 = serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": "Password must be longer than {} characters".format(
                settings.MIN_PASSWORD_LENGTH
            )
        },
    )
    password2 = serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": "Password must be longer than {} characters".format(
                settings.MIN_PASSWORD_LENGTH
            )
        },
    )

    class Meta:
        model = UserModel
        fields = (
            "id",
            "phone_number",
            "email",
            "password1",
            "password2"
        )
        read_only_fields = ("id",)

    def validate(self, data):
        """
        Validates if both password are same or not.
        """
        phone_number = data.get('phone_number')

        if not phone_number.isdigit() or len(phone_number) != 10:
            raise serializers.ValidationError({
                'phone_number': 'Phone number must be 10 digits only.'
            })

        if UserModel.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("Invalid phone number or password.")

        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match")
        return data
    

    def create(self, validated_data):
        """
        Create method.

        Used to create the user
        """
        otp = random.randint(1000, 9999)
        otp_expiry = timezone.now() + timedelta(minutes=10)

        user = UserModel(
            phone_number=validated_data["phone_number"],
            email=validated_data["email"],
            otp=otp,
            otp_expiry=otp_expiry,
            max_otp_try=settings.MAX_OTP_TRY
        )
        user.set_password(validated_data["password1"])
        user.save()
        send_otp(validated_data["phone_number"], otp)
        return user
    
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name']
