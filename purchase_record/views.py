from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from .models import PurchaseVoucher, PurchaseItem
from django.db import transaction, IntegrityError
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PurchaseVoucherForm, PurchaseFormSet, PurchaseItemForm
from inventory.models import Inventory
from django.contrib.postgres.search import TrigramSimilarity
from ledger.models import Ledger, Transaction as LedgerTransaction
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404

# Create your views here.

     



class PurchaseVoucherLedgerAccountSearchView(LoginRequiredMixin, ListView):
    model = Ledger
    template_name = 'purchase_record/voucher.html'
    context_object_name = 'ledgers'
    login_url = "/login/"

    def get_queryset(self):
        query = self.request.GET.get('ledger_search_q', '')

        if not query:
            return Ledger.objects.none()
        
        # search by account name and address fields
        return Ledger.objects.annotate(
            similarity=TrigramSimilarity('account_name', query) + TrigramSimilarity('address', query) + TrigramSimilarity('phone_number', query)
        ).filter(
            business=self.request.user,
            similarity__gt=0.3,
            account_type="Vendor",
        ).order_by('-similarity')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('ledger_search_q'):
            context['searched'] = True
        return context




# get the PurchaseVoucher details and list of items
class PurchaseItemAddView(LoginRequiredMixin, CreateView, ListView, DetailView):
    model = PurchaseItem
    form_class = PurchaseItemForm
    template_name = 'purchase_record/add_items.html'
    context_object_name = 'items'
    login_url = "/login/"


    def get_queryset(self):
        return super().get_queryset().filter(voucher_id=int(self.kwargs['pk']), business=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voucher'] = PurchaseVoucher.objects.get(pk=int(self.kwargs['pk']))
  
        return context

    def form_valid(self, form):
        with transaction.atomic():
            voucher = PurchaseVoucher.objects.get(pk=int(self.kwargs['pk']))
            ledger_id = self.request.GET.get('ledger_id', None)
            ledger = None

            if ledger_id:
                try: 
                    ledger = Ledger.objects.get(pk=int(ledger_id), business=self.request.user)
                except (Ledger.DoesNotExist, ValueError):
                    PurchaseVoucher.objects.filter(pk=voucher.pk, business=self.request.user).delete()
                    return redirect("voucher_search_ledger_account")
            else:
                PurchaseVoucher.objects.filter(pk=voucher.pk, business=self.request.user).delete()
                return redirect("voucher_search_ledger_account")
            
            form.instance.voucher = voucher
            form.instance.business = self.request.user
            form.save()

            preds = Inventory.objects.annotate(similarity=TrigramSimilarity("product_name", form.instance.product_name)).filter(
                similarity__gt=0.5,
                weight=form.instance.weight,
                unit_label=form.instance.weight_label

            ).order_by("-similarity");
            
            # update inventory if exists
            if preds.exists() and preds[0].weight == form.instance.weight:
                Inventory.objects.filter(id=preds[0].id, business=self.request.user).update(
                    quantity= preds[0].quantity + int(form.instance.quantity)
                )
            else:
                # add item in inventory
                Inventory.objects.create(business=self.request.user,
                    product_name=form.instance.product_name,
                    weight=form.instance.weight,
                    unit_label=form.instance.weight_label,
                    quantity=form.instance.quantity)
                
            # create ledger entry
            LedgerTransaction.objects.create(
                business=self.request.user, 
                purchase_voucher=voucher,
                ledger=ledger,
                description=f"Purchase of {form.instance.product_name} (x{form.instance.quantity} bags of {form.instance.weight} {form.instance.weight_label})",
                credit=float(int(form.instance.quantity) * (form.instance.unit_price * form.instance.weight)),
                date=voucher.date,
            )

            return redirect(f'{reverse("add_purchase_item", kwargs={"pk": self.kwargs["pk"]})}?ledger_id={ledger.pk}')
   

class PurchaseVoucherCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseVoucher
    form_class = PurchaseVoucherForm
    template_name = 'purchase_record/create-voucher.html'
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        ledger_id = self.request.GET.get('ledger_id', None)
        if ledger_id:
            
            ledger = Ledger.objects.get(pk=ledger_id, business=self.request.user)

            initial.update({
                "supplier": ledger.account_name,
                "address": ledger.address,
                "phone_number": ledger.phone_number,
            })

        return initial

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.business = self.request.user
            self.object = form.save()


            ledger_id = self.request.POST.get('ledger_id')
            ledger = None

            if ledger_id:
                try:
                    ledger = Ledger.objects.get(pk=int(ledger_id), business=self.request.user)
                except (Ledger.DoesNotExist, ValueError):
                    ledger = None

            if ledger is None:
                # create ledger entry with account creation
                try:
                    ledger = Ledger.objects.create(
                        business=self.request.user,
                        account_name=self.object.supplier,
                        address=self.object.address,
                        phone_number=self.object.phone_number,
                        account_type="Vendor",
                        status="Balanced",
                        note="No dues"
                    )
                except IntegrityError:
                    transaction.set_rollback(True)
                    messages.error(self.request, "Ledger with this account name already exists. Please use a different name.")
                    return redirect(self.request.path)
            return redirect(f'{reverse("add_purchase_item", kwargs={"pk": self.object.pk})}?ledger_id={ledger.pk}')

# complete the purchase voucher
class PurchaseVoucherCompleteView(LoginRequiredMixin, DetailView, ListView):
    model = PurchaseVoucher
    template_name = 'purchase_record/voucher-details.html'
    context_object_name = 'voucher'
    object_list = 'items'
    login_url = "/login/"

    def get_object(self, queryset=None):
        voucher_id = int(self.kwargs.get('pk'))
        voucher = get_object_or_404(self.model, pk=voucher_id, business=self.request.user)
        return voucher
    
    def get(self, request, *args, **kwargs):
        voucher = self.get_object()
        ledger_id = request.GET.get('ledger_id', None)
        ledger = None

        if ledger_id is not None:
            try:
                ledger = Ledger.objects.get(pk=int(ledger_id), business=self.request.user)
            except (Ledger.DoesNotExist, ValueError):
                ledger = None
                messages.error(request, "Ledger not found.")
                return redirect("create_voucher")

        
        if voucher.is_completed:
            messages.error(request, "This voucher has already been completed.")
            return redirect("create_voucher")
        
        voucher.is_completed = True
        voucher.save()


        # update ledger entry if purchased in cash
        if voucher.is_purchased_in_cash:
            ledger = LedgerTransaction.objects.create(
                business=self.request.user, 
                purchase_voucher=voucher,
                ledger=ledger,
                description=f"Cash payment voucher no: {voucher.pk}",
                debit=float(voucher.total_amount),
                date=voucher.date,
            )
        
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        items = PurchaseItem.objects.filter(voucher_id=int(self.kwargs['pk']), business=self.request.user)
        return items
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.get_queryset()
        return context
