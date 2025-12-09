from django.db import models
from ledger.models import Transaction as LedgerTransaction
from inventory.models import Inventory
from django.core.exceptions import ValidationError
from inventory.models import SalesLog

# Create your models here.
class DeliveryOrder(models.Model):
    business = models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    ledger = models.ForeignKey("ledger.Ledger", on_delete=models.CASCADE, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=False, null=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=300, blank=False, null=False)
    total_price = models.FloatField(default=0.0)
    date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False, blank=True, null=True)
    previous_due = models.FloatField(default=0.0)
    grand_total = models.FloatField(default=0.0)
    payment_amount = models.FloatField(default=0.0, blank=True, null=True)
    due_amount = models.FloatField(default=0.0, blank=True, null=True)


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
    
    def save(self, **kwargs):


        # deduct from inventory
        try:
            inventory_product = Inventory.objects.select_for_update().get(business= self.business, product_name=self.product_name)
            if inventory_product.quantity < self.quantity:
                raise ValidationError(
                f"Insufficient inventory for '{self.product_name}'. Available: {inventory_product.quantity}, Requested: {self.quantity}"
            ) 
            inventory_product.quantity -= self.quantity
            inventory_product.save()

            # current day sale log action
            sale_obj, sale_created = SalesLog.objects.get_or_create(
                business=self.business,
                product=inventory_product,
                date__date=self.delivery_order.date,
                defaults={
                    "weight": self.weight,
                    "unit_label": self.unit_label,
                    "quantity_sold": self.quantity,
                    "date": self.delivery_order.date
                }
            )


            
            if not sale_created:
                sale_obj.quantity_sold += self.quantity
                
                sale_obj.save()

            

        except Inventory.DoesNotExist:
            raise ValidationError(f"'{self.product_name}' is not available in inventory.") 

        # create ledger transaction
        LedgerTransaction.objects.create(
            business=self.business,
            ledger=self.delivery_order.ledger,
            sell_voucher=self.delivery_order,
            description=f"Sold {self.product_name} ({self.quantity} bags of {self.weight}{self.unit_label}: {self.total_weight})",
            debit=self.total_price,
            credit=0.0,
            date=self.delivery_order.date,
        )

        return super().save(**kwargs)