from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(TemplateView, LoginRequiredMixin):
    template_name = "home.html"
    login_url = "business_login"