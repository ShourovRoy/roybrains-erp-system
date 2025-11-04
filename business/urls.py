from django.urls import path
from .views import BusinessSignupView, BusinessLoginView

urlpatterns = [
    path('signup/', BusinessSignupView.as_view(), name='business_signup'),
    path('login/', BusinessLoginView.as_view(), name='business_login'),
]
