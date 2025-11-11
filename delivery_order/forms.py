from django.forms import (
    ModelForm, 
    inlineformset_factory, 
    CharField, TextInput, DateTimeField, 
    DateTimeInput, IntegerField, NumberInput,
    FloatField,
    Select, BooleanField, CheckboxInput
)
from .models import DeliveryOrder, DeliveryOrderItem, weight, unit_label

class DeliveryOrderForm(ModelForm):
    date = DateTimeField(widget=DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}), required=True)
    account_name = CharField(widget=TextInput(attrs={'class': 'form-control', 'type': 'text'}), required=True)
    address = CharField(widget=TextInput(attrs={'class': 'form-control', 'type': 'text'}), required=True)
    total_price = FloatField(widget=NumberInput(attrs={'class': 'form-control', 'type': 'number'}), )
    is_paid = BooleanField(widget=CheckboxInput(attrs={'class': 'form-check-input'}), )
    previous_due = FloatField(widget=NumberInput(attrs={'class': 'form-control', 'type': 'number'}), )
    grand_total = FloatField(widget=NumberInput(attrs={'class': 'form-control', 'type': 'number'}), )
    phone_number = CharField(widget=TextInput(attrs={'class': 'form-control', 'type': 'tel'}))
    
    class Meta:
        model = DeliveryOrder
        fields = [
            'account_name',
            'phone_number',
            'address',
            'total_price',
            'date',
            'is_paid',
            'previous_due',
            'grand_total',
        ]

class DeliveryOrderItemForm(ModelForm):
    product_name = CharField(widget=TextInput(attrs={'class': 'form-control py-2'}))
    quantity = IntegerField(widget=NumberInput(attrs={'type': 'number', 'class': 'form-control'}))
    weight = FloatField(widget=Select(attrs={'class': 'form-select'}, choices=weight), required=True)
    unit_label = CharField(widget=Select(attrs={'class': 'form-select'}, choices=unit_label), required=True)
    class Meta:
        model = DeliveryOrderItem
        fields = ["product_name", "quantity", "weight", "unit_label", "price"]
        widgets = {
            'price': NumberInput(attrs={'class': 'form-control'})
        }

DeliveryOrderItemFormSet = inlineformset_factory(
    parent_model=DeliveryOrder, 
    model=DeliveryOrderItem, 
    form=DeliveryOrderItemForm,
    extra=0,
    can_delete=True
)