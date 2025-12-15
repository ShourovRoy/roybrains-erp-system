from django.forms import ModelForm
from .models import ExpenseBook


class ExpenseBookForm(ModelForm):
    class Meta:
        model = ExpenseBook
        exclude = ['business', 'amount']
