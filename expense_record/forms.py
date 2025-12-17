from django.forms import ModelForm, Form, DateTimeInput, ModelChoiceField, CharField, TextInput, FloatField, DateTimeField, NumberInput
from .models import ExpenseLedger, ExpenseLedgerTransaction, EXPENSE_LEDGER_TRANSACTION_STATUS_CHOICES


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
    description = CharField(widget=TextInput(attrs={"placeholder": "Cash", "value": "Cash"}))
    amount = FloatField(widget=NumberInput(attrs={"placeholder": "Enter expense amount"}))
    date = DateTimeField(widget=DateTimeInput(attrs={"type": "datetime-local"}))


    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)


        if business:
            self.fields['select_expense_ledger'].queryset = ExpenseLedger.objects.filter(business=business).order_by("updated_at")