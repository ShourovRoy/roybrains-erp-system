from django.urls import path
from .views import AddCapitalView

app_name = 'capital_management'
urlpatterns = [
    path('add/', AddCapitalView.as_view(), name='add_capital'),
]