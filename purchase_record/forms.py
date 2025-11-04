from django.forms import ModelForm, inlineformset_factory, DateInput, CharField, TextInput, NumberInput, FloatField, Select, DateTimeField, CheckboxInput, BooleanField
from .models import PurchaseVoucher, PurchaseItem
from .models import weight as WEIGHT_CHOICE, weight_label_choice

class PurchaseVoucherForm(ModelForm):
    date = DateTimeField(widget=DateInput(attrs={'type': 'datetime-local', 'placeholder': 'Enter date', 'class': 'form-control', 'required': True}), label="Select Date", required=True)
    supplier = CharField(widget=TextInput(attrs={'type': 'text', 'placeholder': 'Enter supplier name', 'class': 'form-control', 'required': True}), label="Supplier's Name", required=True)
    address = CharField(widget=TextInput(attrs={'type': 'text', 'placeholder': 'Enter address', 'class': 'form-control', 'required': True}), label="Address", required=True)
    phone_number = CharField(widget=TextInput(attrs={'type': 'text', 'placeholder': 'Enter phone number', 'class': 'form-control', 'required': True}), label="Phone Number", required=True)
    is_purchased_in_cash = BooleanField(
        widget=CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Purchased in Cash",
        required=False  # optional, otherwise unchecked box may raise validation error
    )

    class Meta:
        model = PurchaseVoucher
        fields = ['supplier', 'date', 'address', 'phone_number', 'is_purchased_in_cash']

class PurchaseItemForm(ModelForm):
    product_name = CharField(widget=TextInput(attrs={'type': 'text', 'placeholder': 'Enter supplier name', 'class': 'form-control', 'required': True}), required=True)
    quantity = FloatField(widget=NumberInput(attrs={'type': 'number', 'placeholder': '3000.48', 'class': 'form-control', 'value': '0', 'step': '0.01'}, ), required=True)
    weight= FloatField(widget=Select(attrs={'class': 'form-select'}, choices=WEIGHT_CHOICE), label="Select Weight", required=True)
    weight_label = CharField(widget=Select(attrs={'class': 'form-select'}, choices=weight_label_choice), label="Select Weight Label", required=True)
    unit_price = FloatField(widget=NumberInput(attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'placeholder': '87.75'}), required=True, label="Unit Price")

    class Meta:
        model = PurchaseItem
        fields = ['product_name', 'quantity', 'weight', 'weight_label', 'unit_price']
    

PurchaseFormSet = inlineformset_factory(
    PurchaseVoucher,
    PurchaseItem,
    fields=['product_name', 'quantity', 'weight', 'weight_label', 'unit_price'],
    extra=1,
    can_delete=True
)