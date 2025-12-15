from django.db import models

# Create your models here.
class ExpenseBook(models.Model):
    business = models.ForeignKey('business.BusinessUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ExpenseTransaction(models.Model):
    business = models.ForeignKey('business.BusinessUser', on_delete=models.CASCADE)
    expense_book = models.ForeignKey('expense_record.ExpenseBook', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length=255, blank=True, null=True)
    date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    

