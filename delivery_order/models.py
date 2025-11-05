from django.db import models

# Create your models here.
class DeliveryOrder(models.Model):
    business = models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    ledger = models.ForeignKey("ledger.Ledger", on_delete=models.CASCADE, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=False, null=False)
    address = models.CharField(max_length=300, blank=False, null=False)
    