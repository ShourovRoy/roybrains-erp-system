from django.urls import path
from .views import BusinessSignupView, BusinessLoginView, BusinessLogoutView

urlpatterns = [
    path('signup/', BusinessSignupView.as_view(), name='business_signup'),
    path('login/', BusinessLoginView.as_view(), name='business_login'),
    path('logout/', BusinessLogoutView.as_view(), name='business_logout'),
]
