from django.db import models

# Create your models here.
class DeliveryOrder(models.Model):
    business = models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    ledger = models.ForeignKey("ledger.Ledger", on_delete=models.CASCADE, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=False, null=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=300, blank=False, null=False)
    total_price = models.FloatField(default=0.0)
    date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    previous_due = models.FloatField(default=0.0)
    grand_total = models.FloatField(default=0.0)



    def __str__(self):
        return f"DeliveryOrder {self.id} - {self.account_name}"
    

# weight 
weight = {
    (25.0, "25 KG"),
    (26.0, "26 KG"),
    (50.0, "50 KG"),
}

unit_label = {
    ("Kg", "Kilogram"),
}
    
class DeliveryOrderItem(models.Model):
    business = models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    delivery_order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255, blank=False, null=False)
    quantity = models.IntegerField(default=0)
    weight = models.FloatField(choices=weight, default=25.0)
    unit_label = models.CharField(choices=unit_label, max_length=10, default="Kg")
    total_weight = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    total_price = models.FloatField(default=0.0)

    def __str__(self):
        return f"Item {self.product_name} for Order {self.delivery_order.id}"