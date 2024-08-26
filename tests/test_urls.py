from django.test import SimpleTestCase
from django.urls import reverse, resolve
from authentications import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class TestUrls(SimpleTestCase):
    
    def test_admin_url_resolves(self):
        url = reverse('admin:index')
        self.assertEqual(resolve(url).func.__name__, 'index')

    def test_api_auth_url_resolves(self):
        url = reverse('rest_framework:login')
        resolved_func = resolve(url).func
        self.assertTrue(hasattr(resolved_func, 'view_class'))
        self.assertEqual(resolved_func.view_class.__name__, 'LoginView')

    def test_register_user_url_resolves(self):
        url = reverse('register_user')
        self.assertEqual(resolve(url).func, views.register_user)

    def test_verify_email_url_resolves(self):
        url = reverse('verify_email', args=['testtoken'])
        self.assertEqual(resolve(url).func, views.verify_email)

    def test_login_user_url_resolves(self):
        url = reverse('login_user')
        self.assertEqual(resolve(url).func, views.login_user)

    def test_logout_user_url_resolves(self):
        url = reverse('logout_user')
        self.assertEqual(resolve(url).func, views.logout_user)

    def test_token_obtain_pair_url_resolves(self):
        url = reverse('token_obtain_pair')
        self.assertEqual(resolve(url).func.__name__, TokenObtainPairView.as_view().__name__)

    def test_token_refresh_url_resolves(self):
        url = reverse('token_refresh')
        self.assertEqual(resolve(url).func.__name__, TokenRefreshView.as_view().__name__)

    def test_csv_export_url_resolves(self):
        url = reverse('csv_export')
        self.assertEqual(resolve(url).func, views.getfile_csv)

    def test_user_list_url_resolves(self):
        url = reverse('user-list')
        self.assertEqual(resolve(url).func.__name__, 'UserViewSet')

    def test_profile_list_url_resolves(self):
        url = reverse('profile-list')
        self.assertEqual(resolve(url).func.__name__, 'UserProfileViewSet')






