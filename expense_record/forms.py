from django.forms import ModelForm, Form, DateTimeInput, ModelChoiceField, CharField, TextInput, FloatField, DateTimeField, NumberInput, ChoiceField, BooleanField, HiddenInput
from .models import ExpenseLedger, ExpenseLedgerTransaction, EXPENSE_LEDGER_TRANSACTION_STATUS_CHOICES

EXPENSE_MODE = (
    ("cash", "Cash"),
    ("bank", "Bank"),
)

class ExpenseLedgerForm(ModelForm):
    class Meta:
        model = ExpenseLedger
        exclude = ['business', 'amount']

        widgets = {
            'date': DateTimeInput(attrs={'type': 'datetime-local'})
        } 


class ExpenseLedgerTransactionForm(Form):
    select_expense_ledger = ModelChoiceField(
        queryset=ExpenseLedger.objects.filter().none(),
        required=True,
        empty_label="Select Expense",
    )
    expense_source = ChoiceField(choices=EXPENSE_MODE) 
    is_bank_transfered = BooleanField(required=False, initial=False, label="Bank Transfer")
    bank_id = CharField(widget=HiddenInput(attrs={"class": "hidden"}), required=False)
    bank_name = CharField(widget=TextInput(attrs={"class": "hidden", "readonly": True}), required=False)
    description = CharField(widget=TextInput(attrs={"placeholder": "Cash", "value": "Cash"}))
    amount = FloatField(widget=NumberInput(attrs={"placeholder": "Enter expense amount"}))
    date = DateTimeField(widget=DateTimeInput(attrs={"type": "datetime-local"}))


    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)


        if business:
            self.fields['select_expense_ledger'].queryset = ExpenseLedger.objects.filter(business=business).order_by("updated_at")