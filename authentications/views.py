import datetime
import random
from django.conf import settings
from django.utils import timezone 
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .utils import send_otp
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserModel, UserProfile
from .serializers import UserSerializer, UserProfileSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
import csv
import os
from .utils import send_verification_email, generate_verification_token



class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20  
    page_size_query_param = 'page_size'  
    max_page_size = 100 

class UserFilter(filters.FilterSet):
    phone_number = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = UserModel
        fields = ['phone_number', 'email']


class UserViewSet(viewsets.ModelViewSet):
    

    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] 
    pagination_class = CustomPageNumberPagination
    filterset_class = UserFilter
    #throttle_classes = [CustomRateThrottle] 

    @action(detail=True, methods=["PATCH"])
    def verify_otp(self, request, pk=None):
        instance = self.get_object()
        if (
            not instance.is_active
            and instance.otp == request.data.get("otp")
            and instance.otp_expiry
            and timezone.now() < instance.otp_expiry
        ):
            instance.is_active = True
            instance.otp_expiry = None
            instance.max_otp_try = settings.MAX_OTP_TRY
            instance.otp_max_out = None
            instance.save()
            return Response(
                "Successfully verified the user.", status=status.HTTP_200_OK
            )

        return Response(
            "User active or Please enter the correct OTP.",
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["PATCH"])
    def regenerate_otp(self, request, pk=None):
        """
        Regenerate OTP for the given user and send it to the user.
        """
        instance = self.get_object()
        if int(instance.max_otp_try) == 0 and timezone.now() < instance.otp_max_out:
            return Response(
                "Max OTP try reached, try after an hour",
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = random.randint(1000, 9999)
        otp_expiry = timezone.now() + datetime.timedelta(minutes=10)
        max_otp_try = int(instance.max_otp_try) - 1

        instance.otp = otp
        instance.otp_expiry = otp_expiry
        instance.max_otp_try = max_otp_try
        if max_otp_try == 0:
            # Set cool down time
            otp_max_out = timezone.now() + datetime.timedelta(hours=1)
            instance.otp_max_out = otp_max_out
        elif max_otp_try == -1:
            instance.max_otp_try = settings.MAX_OTP_TRY
        else:
            instance.otp_max_out = None
            instance.max_otp_try = max_otp_try
        instance.save()
        send_otp(instance.phone_number, otp)
        return Response("Successfully generate new OTP.", status=status.HTTP_200_OK)
    


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile



@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user.
    """
    email = request.data.get('email')
    phone_number = request.data.get('phone_number')
    password1 = request.data.get('password1')
    password2 = request.data.get('password2')

    # Basic validation
    if not email or not phone_number or not password1 or not password2:
        return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if password1 != password2:
        return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    if UserModel.objects.filter(email=email).exists():
        return Response({'error': 'Email is already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create user
    token = generate_verification_token()
    user = UserModel(
        phone_number=phone_number,
        email=email,
        otp=token,  # Using OTP field to store the verification token
        otp_expiry=now() + timedelta(hours=1),  # Token expires in 1 hour
    )
    user.set_password(password1)
    user.save()

    # Send verification email
    send_verification_email(email, token)

    return Response({'message': 'Registration successful. Please check your email for verification.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, token):
    try:
        user = UserModel.objects.get(otp=token)
        if user.otp_expiry >= now():
            user.is_active = True
            user.otp = ''  
            user.otp_expiry = None
            user.save()
            return JsonResponse({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': 'Token has expired.'}, status=status.HTTP_400_BAD_REQUEST)
    except UserModel.DoesNotExist:
        return JsonResponse({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']
        
        user = get_object_or_404(UserModel, phone_number=phone_number)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getfile_csv(request):
    """
    API view to generate a CSV file with user data and save it locally.
    """
    file_name = "usersname.csv"
    file_path = os.path.join(settings.BASE_DIR, file_name)

    users = UserModel.objects.all()

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Phone Number', 'Email', 'Is Active', 'Date Registered'])
        for user in users:
            writer.writerow([
                user.phone_number,
                user.email,
                user.is_active,
                user.user_registered_at
            ])

    return Response({"message": f"CSV file '{file_name}' has been created successfully."}, status=status.HTTP_200_OK)

