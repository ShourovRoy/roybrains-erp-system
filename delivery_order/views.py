from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ledger.models import Ledger, Transaction as LedgerTransaction
from inventory.models import Inventory
from .models import DeliveryOrder
from django.shortcuts import redirect
from .forms import DeliveryOrderForm, DeliveryOrderItemFormSet
from django.db import transaction
from django.contrib import messages
from django.contrib.postgres.search import TrigramSimilarity
from cashbook.models import CashTransaction
from utils.helper import get_cashbook_on_date_or_previous, get_or_create_journal_book
from journal.models import JournalTransaction


# Create your views here.

# sale management view to 
class SaleManagementView(LoginRequiredMixin, ListView):
    template_name = 'delivery_order/sale-management.html'
    model = Ledger
    login_url = '/login/'
    context_object_name = 'accounts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.GET.get("account_search", None):
            context['searched'] = True

        return context

    def get_queryset(self):
        query = self.request.GET.get('account_search', None)
        if query:
            return super().get_queryset().annotate(
                similarity=TrigramSimilarity('account_name', query) + TrigramSimilarity('address', query) + TrigramSimilarity('phone_number', query)
            ).filter(
                business=self.request.user,
                similarity__gt=0.2,
            )
        return super().get_queryset().none

# create delivery order view
class CreateDeliveryOrderView(LoginRequiredMixin, CreateView):
    template_name = "delivery_order/create-delivery-order.html"
    login_url = '/login/'
    form_class = DeliveryOrderForm
    model = DeliveryOrder
    success_url = "create_delivery_order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"]= DeliveryOrderItemFormSet(self.request.POST, prefix='items')
        else:
            context["formset"] = DeliveryOrderItemFormSet(prefix='items')
        return context
    
    def get_initial(self):
        initial_form = super().get_initial()
        
        # get ledger id 
        ledger_id = self.request.GET.get("ledger_id", None)
        account_details = None
        try:
            if ledger_id:
                account_details = Ledger.objects.get(pk=int(ledger_id), business=self.request.user)

            if account_details:

                # get the last transaction record of the ledger
                # to see if any previous amount is there or not
                # if yes then add it to the default previous due field

                ledger_transactions = LedgerTransaction.objects.filter(ledger=account_details, business=self.request.user).order_by("date", "id")
                last_transaction = ledger_transactions.last() if ledger_transactions.exists() else None

                
                if last_transaction:
                    initial_form.update({
                        'previous_due': last_transaction.balance
                    })

                initial_form.update({
                    'account_name': account_details.account_name,
                    'address': account_details.address,
                    'phone_number': account_details.phone_number,
                })

            return initial_form
        
        except Exception as e:
            messages.error(request=self.request, message=str(e))
            return initial_form
    
    def form_valid(self, form):
        form.instance.business = self.request.user
        context = self.get_context_data()
        formset = context["formset"]

        ledger_id = self.request.POST.get("ledger_id")

        account_details = None

        

        try:
            with transaction.atomic():
                
                if ledger_id:
                    account_details = Ledger.objects.get(pk=int(ledger_id), business=self.request.user)

                if account_details is None:
                    account_details = Ledger.objects.create(
                        business=self.request.user,
                        account_name=form.instance.account_name,
                        address=form.instance.address,
                        phone_number=form.instance.phone_number,
                        account_type="Customer",
                        status="Balanced",
                        note="Just created new account."
                    )

                self.object = form.save(commit=False)
                self.object.ledger = account_details if account_details is not None else None
                self.object.save()

                total_product_price = 0.0

                
                if formset.is_valid():
                    items = formset.save(commit=False)
                    for item in items:
                        item.business = self.request.user
                        item.delivery_order = self.object
                        item.total_weight = item.quantity * item.weight
                        item.total_price = item.price * int(item.quantity)
                        total_product_price = total_product_price + item.total_price
                        
                        item.save()

                    # update total
                    
                    self.object.grand_total = (self.object.previous_due or 0) + self.object.total_price
                    self.object.save()

                    print("previous due: ", self.object.previous_due)
                    print("grand total: ", self.object.grand_total)

                    # insert ledger transaction if any amount is paid
                    if self.object.payment_amount is not None and float(self.object.payment_amount) > 0: 
                        LedgerTransaction.objects.create(
                            business=self.request.user,
                            ledger=account_details,
                            sell_voucher=self.object,
                            description=f"Paid for delivery order no: {self.object.id} on time.",
                            debit=0.00,
                            credit=float(self.object.payment_amount),
                            date=self.object.date
                        )

                        # insert the amount in cashbook
                        cash_book = get_cashbook_on_date_or_previous(self.request.user, self.object.date)

                        # create cash transaction
                        CashTransaction.objects.create(
                            business=self.request.user,
                            cashbook=cash_book,
                            description=f"Received cash payment for Delivery Order no: {self.object.id} from {account_details.account_name}",
                            is_bank=False,
                            debit=float(self.object.payment_amount),
                            credit=0.00,
                            date=self.object.date
                        )

                        # update cash book amount
                        cash_book.cash_amount += float(self.object.payment_amount)
                        cash_book.save()
                    
                    # get journal book
                    journal_book = get_or_create_journal_book(self.request.user, self.object.date)


                    # check if the total bill is 0 then fake order
                    if (float(total_product_price) == float(0)):
                        raise ValueError("Fake order")


                    # start creating journal
                    # journal account debit
                    JournalTransaction.objects.create(
                            business=self.request.user,
                            journal=journal_book,
                            ledger_ref=account_details,
                            description=f"{account_details.account_name.capitalize()} - {account_details.address}",
                            debit=float(total_product_price),
                            credit=0.00,
                            date=self.object.date
                        )
                    # journal sales credit
                    JournalTransaction.objects.create(
                            business=self.request.user,
                            journal=journal_book,
                            description=f"Sales - x{len(items)}",
                            debit=0.00,
                            credit=float(total_product_price),
                            date=self.object.date
                        )
                        
                       
                    # check if the sale is paid with exact amount
                    if (float(self.object.payment_amount) == float(total_product_price) and (float(self.object.payment_amount)> 0 and float(total_product_price) > 0)):

                        print("---paid---")

                        # journal cash debit (with voucher id)
                        JournalTransaction.objects.create(
                            business=self.request.user,
                            journal=journal_book,
                            description="Cash",
                            debit=float(total_product_price),
                            credit=0.00,
                            date=self.object.date
                        )


                        # journal account credit (with voucher id)
                        JournalTransaction.objects.create(
                            business=self.request.user,
                            journal=journal_book,
                            ledger_ref=account_details, 
                            description=f"{account_details.account_name.capitalize()} - {account_details.address}",
                            debit=0.00,
                            credit=float(total_product_price),
                            date=self.object.date
                        )

                
                    
                    # check if the payment amount is less than the actual sale amount
                    if ((float(self.object.payment_amount) < float(total_product_price)) and (self.object.payment_amount is not None and float(self.object.payment_amount) > 0)):

                        print("---partial paid---")

                        # journal cash debit (paid cash amount)
                        JournalTransaction.objects.create(
                            business=self.request.user,
                            journal=journal_book,
                            description="Cash",
                            debit=float(total_product_price - self.object.payment_amount),
                            credit=0.00,
                            date=self.object.date
                        )

                        # journal accounts credit (with voucher id)
                        JournalTransaction.objects.create(
                            business=self.request.user,
                            journal=journal_book,
                            ledger_ref=account_details,
                            description=f"{account_details.account_name.capitalize()} - {account_details.address}",
                            debit=0.00,
                            credit=float(total_product_price - self.object.payment_amount),
                            date=self.object.date
                        )


                    # check if the payment amount is more than the actual sale amount
                    if (float(self.object.payment_amount) > float(total_product_price)):

                        # journal cash debit (payment amount - sales amount)
                        JournalTransaction.objects.create(
                            business=self.request.user,
                            journal=journal_book,
                            description="Cash",
                            debit=float(self.object.payment_amount),
                            credit=0.00,
                            date=self.object.date
                        )
                        # journal accounts credit (payment amount - sales amount)
                        JournalTransaction.objects.create(
                            business=self.request.user,
                            journal=journal_book,
                            ledger_ref=account_details,
                            description=f"{account_details.account_name.capitalize()} - {account_details.address}",
                            debit=0.00,
                            credit=float(self.object.payment_amount),
                            date=self.object.date
                        )

        except Exception as e :
            messages.warning(request=self.request, message=f"{e}")
                
            return self.form_invalid(form)
        
        messages.success(request=self.request, message=f"Delivery Order has been created.")

        return redirect("create_delivery_order")

# search product in delivery order page through htmx ajax call view
class SearchInventoryProductView(LoginRequiredMixin, ListView):
    template_name = "delivery_order/partials/search-result.html"
    model = Inventory
    context_object_name = "products"

    def get_queryset(self):
        query = self.request.GET.get("product_search", "")

        if query:
            return super().get_queryset().annotate(similarity=TrigramSimilarity("product_name", query)).filter(similarity__gt=0.2, business=self.request.user).order_by("id")
         
        return []


# list delivery orders view
class DeliveryOrdersList(LoginRequiredMixin, ListView):
    template_name = "delivery_order/delivery-orders-list.html"
    login_url = "/login/"
    model = DeliveryOrder
    context_object_name = "delivery_orders"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        q = self.request.GET.get("delivery_order_id", None)

        if q is not None:
            context['is_searched'] = True

        return context


    def get_queryset(self):

        q = self.request.GET.get("delivery_order_id", None)

        if self.request.GET.get("delivery_order_id"):
            return super().get_queryset().filter(business=self.request.user, pk=q).order_by('date', 'id')


        return super().get_queryset().filter(business=self.request.user, total_price__gt=0.0).order_by('date', 'id')
    
