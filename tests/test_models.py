import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError
from authentications.models import UserModel, UserProfile

@pytest.mark.django_db
class TestUserModel:

    def test_create_user(self):
        user = UserModel.objects.create_user(phone_number='1234567890', password='checkpassword')
        assert user.phone_number == '1234567890'
        assert user.check_password('checkpassword')
        assert user.is_active is False
        assert not user.is_staff

    def test_create_superuser(self):
        user = UserModel.objects.create_superuser(phone_number='0987654321', password='superpassword')
        assert user.phone_number == '0987654321'
        assert user.check_password('superpassword')
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_phone_number_validation(self):
        with pytest.raises(ValidationError):
            user = UserModel(phone_number='12345', password='checkpassword')
            user.full_clean()  # This will trigger validation

    def test_otp_expiry(self):
        now = timezone.now()
        user = UserModel(phone_number='1234567890', password='checkpassword', otp_expiry=now)
        user.set_password('checkpassword')  # Ensure password is hashed
        user.save()
        user.refresh_from_db()  # Refresh to get the latest data
        assert user.otp_expiry == now

@pytest.mark.django_db
class TestUserProfileModel:

    def test_create_user_profile(self):
        user = UserModel.objects.create_user(phone_number='1234567890', password='checkpassword')
        profile = UserProfile.objects.create(user=user, first_name='pooji', last_name='tha', address='123 wxyz St')
        assert profile.user == user
        assert profile.first_name == 'pooji'
        assert profile.last_name == 'tha'
        assert profile.address == '123 wxyz St'

    def test_user_profile_unique_constraint(self):
        user = UserModel.objects.create_user(phone_number='1234567890', password='checkpassword')
        UserProfile.objects.create(user=user, first_name='minnu', last_name='reddy', address='456 wxyz St')
        with pytest.raises(Exception):
            UserProfile.objects.create(user=user, first_name='minnu', last_name='reddy', address='456 wxyz St')
