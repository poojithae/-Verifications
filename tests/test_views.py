import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from authentications.models import UserModel, UserProfile

@pytest.mark.django_db
class TestUserViews:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserModel.objects.create_user(
            phone_number='1234567890',
            #email='test@example.com',
            password='checkpassword'
        )
        self.client.force_authenticate(user=self.user)

        self.superuser = UserModel.objects.create_superuser(
            phone_number='0987654321',
            password='superpassword'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            first_name='pooji',
            last_name='tha',
            address='123 wxyz St'
        )
        self.register_url = reverse('register_user')
        self.login_url = reverse('login_user')
        self.verify_email_url = reverse('verify_email', args=['dummy-token'])
        self.getfile_csv_url = reverse('csv_export')

    def test_register_user(self):
        response = self.client.post(self.register_url, {
            'email': 'newuser@example.com',
            'phone_number': '9876543210',
            'password1': 'password123',
            'password2': 'password123'
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert 'message' in response.data

    def test_login_user(self):
        response = self.client.post(self.login_url, {
            'phone_number': '1234567890',
            'password': 'checkpassword'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_verify_email(self):
        token = 'dummy-token'
        response = self.client.get(reverse('verify_email', args=[token]))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.json()

    def test_getfile_csv(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(self.getfile_csv_url)
        assert response.status_code == status.HTTP_200_OK
        assert "CSV file 'usersname.csv' has been created successfully." in response.data['message']

    def test_otp_verification(self):
        # Set up the OTP for the user
        self.user.otp = '123456'
        self.user.otp_expiry = timezone.now() + timedelta(minutes=5)
        self.user.save()

        response = self.client.patch(reverse('user-verify-otp', args=[self.user.pk]), {'otp': '123456'})
        assert response.status_code == status.HTTP_200_OK
        assert "Successfully verified the user." in response.data

    def test_regenerate_otp(self):
        self.client.force_authenticate(user=self.user)
        self.user.max_otp_try = 1
        self.user.otp_expiry = timezone.now() + timedelta(minutes=5)
        self.user.save()

        response = self.client.patch(reverse('user-regenerate-otp', args=[self.user.pk]))
        assert response.status_code == status.HTTP_200_OK
        assert "Successfully generate new OTP." in response.data

    def test_user_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('userprofile-detail', args=[self.user.pk]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'John'
        assert response.data['last_name'] == 'Doe'
        assert response.data['address'] == '123 Main St'
        
    def test_user_profile_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(reverse('user_profile', args=[self.user.pk]), {
            'first_name': 'pooji',
            'last_name': 'tha',
            'address': '456 wxyz St'
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'pooji'
        assert response.data['last_name'] == 'tha'
        assert response.data['address'] == '456 wzxy St'

@pytest.mark.django_db
class TestAuthenticationViews:
    def test_login_user_invalid(self):
        client = APIClient()
        response = client.post(reverse('login_user'), {
            'phone_number': '1234567890',
            'password': 'wrongpassword'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_missing_fields(self):
        client = APIClient()
        response = client.post(reverse('register_user'), {
            'email': 'newuser@example.com',
            'phone_number': '9876543210',
            'password1': 'password123'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_verify_email_invalid_token(self):
        client = APIClient()
        response = client.get(reverse('verify_email', args=['invalid-token']))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.json()
