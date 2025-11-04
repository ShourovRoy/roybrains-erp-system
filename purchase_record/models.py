from django.db import models
from ledger.models import Transaction as LedgerTransaction
# Create your models here.

# weight choice
weight_label_choice = {
    'kg': 'Kilogram',
}

# weight choices tuple
weight = {
    25: '25',
    50: '50',
    26: '26',
}



class PurchaseVoucher(models.Model):
    business = models.ForeignKey(to="business.BusinessUser", on_delete=models.CASCADE)
    supplier = models.CharField(max_length=255)
    address = models.TextField(max_length=500, blank=True, null=True)
    phone_number = models.CharField(max_length=14, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateTimeField()
    is_purchased_in_cash = models.BooleanField(default=False, blank=True, null=True)
    is_completed = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.supplier
    

class PurchaseItem(models.Model):
    voucher = models.ForeignKey(to=PurchaseVoucher, on_delete=models.CASCADE, related_name='items')
    business = models.ForeignKey(to="business.BusinessUser", on_delete=models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=0)
    weight = models.FloatField(max_length=10,  choices=weight, default=0.00)
    weight_label = models.CharField(max_length=10, choices=weight_label_choice, default='kg')
    unit_price = models.FloatField(max_length=10,  default=0.00)
    item_price = models.FloatField(max_length=10,  default=0.00)

    def __str__(self):
        return f"{self.product_name} - {self.quantity} @ {self.unit_price}"
    
    def save(self, **kwargs):
        self.item_price = self.quantity * (self.unit_price * self.weight)

        items = PurchaseItem.objects.filter(voucher=self.voucher, business=self.voucher.business)
        total_voucher_amount = 0 + self.item_price

        for item in items:
            total_voucher_amount += item.item_price

        # update total amount in voucher
        PurchaseVoucher.objects.filter(pk=self.voucher.pk).update(total_amount=total_voucher_amount)


        return super().save(**kwargs)