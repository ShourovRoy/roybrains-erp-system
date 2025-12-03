from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from .models import BusinessUser
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class BusinessSignupView(TemplateView):

    template_name = "business/signup.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/inventory')  # Redirect to a dashboard or home page if already logged in
        return render(request, self.template_name)
    
    def post(self, request):
        business_name = request.POST.get('business_name')
        business_address = request.POST.get('business_address')
        contact_number = request.POST.get('contact_number')
        owner_name = request.POST.get('owner_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = BusinessUser.objects.create_user(
            username=email + owner_name,
            business_name=business_name,
            business_address=business_address,
            contact_number=contact_number,
            owner_name=owner_name,
            email=email,
        )
        user.set_password(password)
        user.save()

        return render(request, 'business/login.html')
    
class BusinessLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/inventory')  # Redirect to a dashboard or home page if already logged in
        return render(request, 'business/login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('/inventory')
        else:
            return render(request, 'business/login.html')
        

# logout view
class BusinessLogoutView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        logout(request)
        return redirect('business_login')
    
