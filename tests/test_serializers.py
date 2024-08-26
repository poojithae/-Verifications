import pytest
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from authentications.models import UserModel, UserProfile
from authentications.serializers import UserSerializer, LoginSerializer, UserProfileSerializer

User = get_user_model()

@pytest.mark.django_db
class TestUserSerializer:
    @pytest.fixture
    def user_data(self):
        return {
            'phone_number': '1234567897',
            'email': 'user@gmail.com',
            'password1': 'pass1234',
            'password2': 'pass1234',
        }
    
    def test_user_serializer_valid(self, user_data):
        serializer = UserSerializer(data=user_data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert UserModel.objects.get(phone_number=user_data['phone_number']) == user

    def test_user_serializer_invalid_password_mismatch(self, user_data):
        user_data['password2'] = 'differentpassword'
        serializer = UserSerializer(data=user_data)
        assert not serializer.is_valid()
        assert 'Passwords do not match' in str(serializer.errors)

    def test_user_serializer_invalid_phone_number(self, user_data):
        user_data['phone_number'] = 'invalid'
        serializer = UserSerializer(data=user_data)
        assert not serializer.is_valid()
        assert 'Phone number must be 10 digits only.' in str(serializer.errors)

    def test_user_serializer_invalid_password_length(self, user_data):
        user_data['password1'] = 'short'
        user_data['password2'] = 'short'
        serializer = UserSerializer(data=user_data)
        assert not serializer.is_valid()
        assert 'Password must be longer than' in str(serializer.errors)

    def test_user_serializer_missing_field(self):
        user_data = {
            'phone_number': '1234567890',
            'email': 'user@gmail.com',
            'password1': 'password123',
            # password2 is missing
        }
        serializer = UserSerializer(data=user_data)
        assert not serializer.is_valid()
        assert 'password2' in serializer.errors

    
@pytest.mark.django_db
class TestUserProfileSerializer:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            phone_number='1234567890',
            password='password123'
        )

    @pytest.fixture
    def user_profile(self, user):
        return UserProfile.objects.create(
            user=user,
            first_name='pooji',
            last_name='tha'
        )

    def test_user_profile_serializer(self, user_profile):
        serializer = UserProfileSerializer(user_profile)
        assert serializer.data == {
            'first_name': 'pooji',
            'last_name': 'tha'
        }


