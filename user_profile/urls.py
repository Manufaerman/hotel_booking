from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import register, contact, ChangeUsername,\
    profile, clients, thanks, login

app_name = 'user_profile'
urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('contact/', contact, name='contact'),
    path('clients/', clients, name='clients'),
    path('profile/', profile, name='profile'),
    path('accounts/change-username/', ChangeUsername.as_view(), name='account_change_username'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('accounts/signup/thanks/', thanks, name='thanks')

] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)