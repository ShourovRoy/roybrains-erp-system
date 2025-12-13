from django.urls import path
from .views import PurchaseVoucherCreateView, PurchaseItemAddView, PurchaseVoucherLedgerAccountSearchView, PurchaseVoucherCompleteView, PurchaseVoucherListView

urlpatterns = [
    path('voucher-search-ledger-account/', PurchaseVoucherLedgerAccountSearchView.as_view(), name='voucher_search_ledger_account'),
    path('create-voucher/', PurchaseVoucherCreateView.as_view(), name='create_voucher'),
    path('add-purchase-item/<int:pk>', PurchaseItemAddView.as_view(), name='add_purchase_item'),
    path('complete-voucher/<int:pk>/', PurchaseVoucherCompleteView.as_view(), name='complete_voucher'),
    path('voucher-list/', PurchaseVoucherListView.as_view(), name="purchase_voucher_list"),
]