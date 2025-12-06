from django.shortcuts import redirect
from django.views.generic import CreateView
from .models import Capital, CapitalTransaction
from .forms import CapitalTransactionForm
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

class AddCapitalView(LoginRequiredMixin, CreateView):
    template_name = 'capital_management/add-capital.html'
    model = CapitalTransaction
    form_class = CapitalTransactionForm
    login_url = "/login/"

    def form_valid(self, form):
        # Add any custom processing here if needed
        form.instance.user = self.request.user

        # TODO: 6-12-25 check if any capital exists for the business user
        capital_obj, capital_created = Capital.objects.get_or_create(business=self.request.user.businessuser)


        return super().form_valid(form)