from django.forms import ModelForm, formset_factory, DateInput, Form, Select, CharField, TextInput, HiddenInput



# capital transaction form
class CapitalForm(Form):
    transaction_type = CharField(widget=Select(choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal')]), label='Transaction Type')
    invest_in = CharField(widget=Select(choices=[('bank', 'Bank'), ('cash', 'Cash')]), label='Invest In')
    amount = CharField(label='Amount', max_length=20)
    date = CharField(widget=DateInput(attrs={'type': 'datetime-local'}), label='Date')
    bank_account_id = CharField(widget=TextInput(attrs={'id': 'id_bank_account', 'class': 'show'}), label=None, required=False)
