from django.views.generic import TemplateView, ListView, UpdateView, DetailView, CreateView
from ledger.models import Ledger, Transaction as LedgerTransaction
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import datetime
# Create your views here.

# financial control panel
class FinanceFlowView(LoginRequiredMixin,TemplateView):
    template_name = "finance_flow/finance-flow-control.html"
    login_url = "/login/"

# search accounts
class FincialAccountSearchView(LoginRequiredMixin, ListView):
    template_name = "finance_flow/partials/account-search-result.html"
    model = Ledger
    context_object_name = 'accounts'
    login_url = "/login/"

    def get_queryset(self):
        query = self.request.GET.get("search_query", None)

        if query:
            return super().get_queryset().annotate(
                 similarity=TrigramSimilarity('account_name', query) + TrigramSimilarity(Coalesce('address', Value('')), query) + TrigramSimilarity(Coalesce('branch', Value('')), query)
                + TrigramSimilarity(Coalesce('phone_number', Value('')), query)
            ).filter(
                business=self.request.user,
                similarity__gt=0.2,
            )
        return super().get_queryset().none

# financial inflow panel
class FinancialInflowView(LoginRequiredMixin, DetailView):
    login_url = "/login"
    model = Ledger
    template_name = "finance_flow/finance-incoming-flow.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['leder_details'] = self.model.objects.get(business=self.request.user, pk=int(self.kwargs['pk']))

        return context
    
# take amount in full cash
class FinancialCashInFlow(LoginRequiredMixin, CreateView):
    template_name = "finance_flow/incoming-full-cash.html"
    login_url = "/login/"
    model = LedgerTransaction
    fields = []
    
    def form_valid(self, form):

        ledger_id = int(self.kwargs["pk"])

        amount = float(self.request.POST.get("amount"))
        date_time = self.request.POST.get("datetime")
        
        try:
            date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
        except ValueError:
            form.add_error(None, "Invalid date format.")
            return self.form_invalid(form)

        try:


            ledger = Ledger.objects.get(business=self.request.user, pk= ledger_id)

            if ledger:

                self.model.objects.create(
                    business=self.request.user,
                    ledger=ledger,
                    credit=amount,
                    debit=0.0,
                    description=f"{ledger.account_name} cash",
                    date=date_time
                )

            return redirect("ledger-transaction-list", pk=ledger_id)

        except Exception as e:
            print(e)
            messages.error(request=self.request, message="Something went wrong! Try again")
            return redirect("financial-inflow-cash", pk=ledger_id)

# financial bank in flow search
class FinancialBankInFlow(LoginRequiredMixin, DetailView):
    login_url = "/login/"
    model = Ledger
    template_name = "finance_flow/incoming-full-bank-search.html"
    context_object_name = "account"


    def get_object(self, queryset = None):
        account_id = int(self.kwargs['pk'])

        return get_object_or_404(self.model, business=self.request.user, pk=account_id)
    
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        query = self.request.GET.get("search_bank", None)
       
        if query:
            banks = Ledger.objects.annotate(
                similarity=TrigramSimilarity("account_name", query),
            ).filter(business=self.request.user, similarity__gt=0.3, branch__isnull=False, ).exclude(branch="").order_by("-similarity")

            context['items'] = banks
        else:
             context['items'] = []
        return context
    

# financial bank in flow action
class FinancialBankInflowActionView(LoginRequiredMixin, CreateView):
    login_url = "/login/"
    template_name = "finance_flow/incoming-full-bank-deposite.html"
    model = LedgerTransaction
    fields = []

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        account_id = int(self.kwargs["pk"])
        bank_id = int(self.kwargs["bank_id"])

        context['account'] = get_object_or_404(Ledger, business=self.request.user, pk=account_id)
        context['bank_details'] = get_object_or_404(Ledger, business=self.request.user, pk=bank_id)

        return context
        

    def form_valid(self, form):

        amount = float(self.request.POST.get("amount"))
        date_time = self.request.POST.get("datetime")

        account_id = int(self.kwargs["pk"])
        bank_id = int(self.kwargs["bank_id"])

        try:
            date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
        except ValueError:
            form.add_error(None, "Invalid date format.")
            return self.form_invalid(form)



        try:
        
            with transaction.atomic():
                account_ledger = get_object_or_404(Ledger, business=self.request.user, pk=account_id)
                bank_ledger = get_object_or_404(Ledger, business=self.request.user, pk=bank_id)

                # create the ledger transactions
                # account credit
                self.model.objects.create(
                    business=self.request.user,
                    ledger=account_ledger,
                    description=f"Deposite at {bank_ledger.account_name} - {bank_ledger.branch}",
                    date=date_time,
                    credit=float(amount),
                    debit=0.0
                )

                # bank debit
                self.model.objects.create(
                    business=self.request.user,
                    ledger=bank_ledger,
                    description=f"Money came from {account_ledger.account_name} - {account_ledger.address}",
                    date=date_time,
                    debit=float(amount),
                    credit=0.0
                )

                messages.success(request=self.request, message="Action done successfully")
                return redirect("ledger-list")

        except Exception as e:
            print(e)
            messages.error(request=self.request, message="Action failed! Try again.")
            return self.form_invalid(form)

# financial bank and cash partial inflow
class FinancialPartialInflowView(LoginRequiredMixin, DetailView):
    login_url = "/login/"
    template_name = "finance_flow/incoming-partial-flow-search.html"
    model = Ledger

    context_object_name = 'account'

    def get_object(self, queryset = None):
        account_id = int(self.kwargs['pk'])

        return get_object_or_404(self.model, business=self.request.user, pk=account_id)
    
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        query = self.request.GET.get("search_bank", None)
       
        if query:
            banks = Ledger.objects.annotate(
                similarity=TrigramSimilarity("account_name", query),
            ).filter(business=self.request.user, similarity__gt=0.3, branch__isnull=False, ).exclude(branch="").order_by("-similarity")

            context['items'] = banks
        else:
             context['items'] = []
        return context
    
# financial bank and cash inflow action
class FinancialPartialInflowActionView(LoginRequiredMixin, CreateView, DetailView):
    login_url = "/login/"
    model = Ledger
    template_name = "finance_flow/incoming-partial-flow-action.html"
    fields = []
    context_object_name = "account"

    def get_object(self, queryset = ...):
        account_id = int(self.kwargs["pk"])
        return get_object_or_404(self.model, business=self.request.user, pk=account_id);

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bank_id = int(self.kwargs["bank_id"])

        context['bank_details'] = get_object_or_404(Ledger, business=self.request.user, pk=bank_id)

        return context;

    def form_valid(self, form):

        account_id = int(self.request.POST.get("account_id"))
        bank_id = int(self.request.POST.get("bank_id"))


        # get the cash amount and bank amount
        cash_amount = float(self.request.POST.get("cash_amount", 0.0))
        bank_amount = float(self.request.POST.get("bank_amount", 0.0))

        # get the date
        date_time = self.request.POST.get("datetime")

        try:
            date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
        except ValueError:
            form.add_error(None, "Invalid date format.")
            return self.form_invalid(form)
        
        try:


            with transaction.atomic():
                account_ledger = get_object_or_404(self.model, business=self.request.user, pk=account_id)
                bank_ledger = get_object_or_404(self.model, business=self.request.user, pk=bank_id)
                
                # accounts credit in cash
                LedgerTransaction.objects.create(
                    business=self.request.user,
                    ledger=account_ledger,
                    description="Gave cash in liquide",
                    debit=0.0,
                    credit=cash_amount,
                    date=date_time,
                )
                LedgerTransaction.objects.create(
                    business=self.request.user,
                    ledger=account_ledger,
                    description=f"Deposited in {bank_ledger.account_name} - {bank_ledger.branch}",
                    debit=0.0,
                    credit=bank_amount,
                    date=date_time,
                )

                # bank debit 
                LedgerTransaction.objects.create(
                    business=self.request.user,
                    ledger=bank_ledger,
                    description=f"{account_ledger.account_name} - {account_ledger.address} deposited",
                    debit=bank_amount,
                    credit=0.0,
                    date=date_time,
                )



                messages.info(request=self.request, message="Ledger transaction has been sucessfull.")

                return redirect("ledger-list")

        except Exception as e:
            print(e)
            messages.error(request=self.request, message="Action failed please try again!")
            return redirect("fnancial-inflow-partial-action", pk=account_id, bank_id=bank_id)
        


# finance outflow starts here
# finance outflow view
class FinancialOutflowView(LoginRequiredMixin, DetailView):
    template_name = "finance_flow/financial-outgoing-flow.html"
    model = Ledger
    login_url = "/login/"
    context_object_name = "ledger"

    def get_object(self, queryset = ...):
        try:
            account_id = int(self.kwargs["pk"])
            return get_object_or_404(self.model, business=self.request.user, pk=account_id)
        except Exception as e:
            print(e)
            messages.warning(request=self.request, message="Invalid account id!")
            return redirect("finance-flow")
        
# give full money in cash view
class FinancialOutflowInCashView(LoginRequiredMixin, CreateView):
    login_url = "/login/"
    model = LedgerTransaction
    fields = []
    template_name = "finance_flow/outgoing-full-cash.html"

    def form_valid(self, form):

        try:
            account_id = int(self.kwargs["pk"])
        except Exception as e:
            print(e)
            messages.warning(request=self.request, message="Invalid account id!")
        
        try:
            
            # extract data from form
            cash_amount = float(self.request.POST.get("cash_amount", 0.0))
            date_time = self.request.POST.get("datetime", None)

            if date_time:
                date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
            else:
                messages.error(request=self.request, message="Need a date to complete the action!")
                return self.form_invalid(form)

            with transaction.atomic():
                # get ledger details 
                ledger_details = get_object_or_404(Ledger, business=self.request.user, pk=account_id)

                # make ledger entry
                LedgerTransaction.objects.create(
                    business=self.request.user, 
                    ledger=ledger_details,
                    debit=cash_amount,
                    credit=0.0,
                    description="Cash given in liquide",
                    date=date_time,
                )

                messages.success(request=self.request, message=f"Cash given sucessfully to {ledger_details.account_name} - {ledger_details.address}")

                return redirect("ledger-transaction-list", pk=ledger_details.pk)

        except Exception as e:
            messages.error(request=self.request, message="Something went wrong!")  
            return self.form_invalid(form);


# give full money bank serach
class FinancialOutflowBankSearchView(LoginRequiredMixin, DetailView):
    login_url = "/login"
    template_name = "finance_flow/outgoing-full-bank-search.html"
    model = Ledger
    context_object_name = "account"

    def get_object(self, queryset = ...):
        account_id = int(self.kwargs['pk'])

        return get_object_or_404(self.model, business=self.request.user, pk=account_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        query = self.request.GET.get("search_bank", None)
       
        if query:
            banks = Ledger.objects.annotate(
                similarity=TrigramSimilarity("account_name", query),
            ).filter(business=self.request.user, similarity__gt=0.3, branch__isnull=False, ).exclude(branch="").order_by("-similarity")

            context['items'] = banks
        else:
             context['items'] = []
        return context
    

class FinancialOutflowBankActionView(LoginRequiredMixin, CreateView):
    login_url = "/login/"
    model = LedgerTransaction
    fields = []
    template_name = "finance_flow/outgoing-full-bank-out.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bank_id = int(self.kwargs["bank_id"])
        account_id = int(self.kwargs["pk"])

        context['account'] = get_object_or_404(Ledger, business=self.request.user, pk=account_id)
        context['bank_details'] = get_object_or_404(Ledger, business=self.request.user, pk=bank_id)


        return context
    

    def form_valid(self, form):

        amount = float(self.request.POST.get("amount"))
        date_time = self.request.POST.get("datetime")

        account_id = int(self.kwargs["pk"])
        bank_id = int(self.kwargs["bank_id"])

        try:
            date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
        except ValueError:
            form.add_error(None, "Invalid date format.")
            return self.form_invalid(form)



        try:
        
            with transaction.atomic():
                account_ledger = get_object_or_404(Ledger, business=self.request.user, pk=account_id)
                bank_ledger = get_object_or_404(Ledger, business=self.request.user, pk=bank_id)

                # create the ledger transactions
                # account debit
                self.model.objects.create(
                    business=self.request.user,
                    ledger=account_ledger,
                    description=f"Transferred from {bank_ledger.account_name} - {bank_ledger.branch}",
                    date=date_time,
                    debit=float(amount),
                    credit=0.0
                )

                # bank debit
                self.model.objects.create(
                    business=self.request.user,
                    ledger=bank_ledger,
                    description=f"Money has been sent to {account_ledger.account_name} - {account_ledger.address}",
                    date=date_time,
                    credit=float(amount),
                    debit=0.0
                )

                messages.success(request=self.request, message="Action done successfully")
                return redirect("ledger-transaction-list", pk=account_id)

        except Exception as e:
            print(e)
            messages.error(request=self.request, message="Action failed! Try again.")
            return self.form_invalid(form)


# search partial outflow search with bank and cash
class FinancialPartialOutflowSearchView(LoginRequiredMixin, DetailView):
    login_url = "/login/"
    template_name = "finance_flow/outgoing-partial-flow-search.html"
    model = Ledger
    context_object_name = "account"

    def get_object(self, queryset = None):
        account_id = int(self.kwargs['pk'])

        return get_object_or_404(self.model, business=self.request.user, pk=account_id)
    
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        query = self.request.GET.get("search_bank", None)
       
        if query:
            banks = Ledger.objects.annotate(
                similarity=TrigramSimilarity("account_name", query),
            ).filter(business=self.request.user, similarity__gt=0.3, branch__isnull=False, ).exclude(branch="").order_by("-similarity")

            context['items'] = banks
        else:
             context['items'] = []
        return context
    

# partial outflow with bank and cash action
class FinancialPartialOutflowActionView(LoginRequiredMixin, CreateView, DetailView):
    login_url = "/login/"
    model = Ledger
    template_name = "finance_flow/outgoing-partial-flow-action.html"
    fields = []
    context_object_name = "account"

    def get_object(self, queryset = ...):
        account_id = int(self.kwargs["pk"])
        return get_object_or_404(self.model, business=self.request.user, pk=account_id);

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bank_id = int(self.kwargs["bank_id"])

        context['bank_details'] = get_object_or_404(Ledger, business=self.request.user, pk=bank_id)

        return context;

    def form_valid(self, form):

        account_id = int(self.request.POST.get("account_id"))
        bank_id = int(self.request.POST.get("bank_id"))


        # get the cash amount and bank amount
        cash_amount = float(self.request.POST.get("cash_amount", 0.0))
        bank_amount = float(self.request.POST.get("bank_amount", 0.0))

        # get the date
        date_time = self.request.POST.get("datetime")

        try:
            date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
        except ValueError:
            form.add_error(None, "Invalid date format.")
            return self.form_invalid(form)
        
        try:


            with transaction.atomic():
                account_ledger = get_object_or_404(self.model, business=self.request.user, pk=account_id)
                bank_ledger = get_object_or_404(self.model, business=self.request.user, pk=bank_id)
                
                # accounts credit in cash
                LedgerTransaction.objects.create(
                    business=self.request.user,
                    ledger=account_ledger,
                    description="Cash given in liquide",
                    credit=0.0,
                    debit=cash_amount,
                    date=date_time,
                )
                LedgerTransaction.objects.create(
                    business=self.request.user,
                    ledger=account_ledger,
                    description=f"Given from {bank_ledger.account_name} - {bank_ledger.branch}",
                    credit=0.0,
                    debit=bank_amount,
                    date=date_time,
                )

                # bank debit 
                LedgerTransaction.objects.create(
                    business=self.request.user,
                    ledger=bank_ledger,
                    description=f"Money given to {account_ledger.account_name} - {account_ledger.address}",
                    credit=bank_amount,
                    debit=0.0,
                    date=date_time,
                )

                messages.info(request=self.request, message="Ledger transaction has been sucessfull.")

                return redirect("financial-outflow", pk=account_id)

        except Exception as e:
            print(e)
            messages.error(request=self.request, message="Action failed please try again!")
            return redirect("fnancial-inflow-partial-action", pk=account_id, bank_id=bank_id)
        
