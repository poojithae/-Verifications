import requests
from django.conf import settings
from django.core.mail import send_mail
import uuid


def send_otp(mobile, otp):
    """
    Send message.
    """
    url = f"https://2factor.in/API/V1/{settings.SMS_API_KEY}/SMS/{mobile}/{otp}/Your OTP is"
    payload = ""
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.get(url, data=payload, headers=headers)
    return bool(response.ok)


def generate_verification_token():
    return str(uuid.uuid4())

# Send verification email
def send_verification_email(user_email, token):
    verification_link = f"{settings.SITE_URL}/api/verify-email/{token}/"
    send_mail(
        'Verify your email',
        f'Please click the following link to verify your email address: {verification_link}',
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )



