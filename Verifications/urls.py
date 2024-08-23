"""
URL configuration for Verifications project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from authentications import views

router = DefaultRouter()
router.register("users", views.UserViewSet, basename="user")
router.register("profiles", views.UserProfileViewSet, basename="profile")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('api/register/', views.register_user, name='register_user'),
    path('api/verify-email/<token>/', views.verify_email, name='verify_email'),
    path('api/login/', views.login_user, name='login_user'),
    path('api/logout/', views.logout_user, name='logout_user'),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/csv/', views.getfile_csv, name='csv_export'),
    
    # path('api/password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    # path('api/password-reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('api/password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('api/password-reset/complete/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
]

