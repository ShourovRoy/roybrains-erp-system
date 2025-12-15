from django.db import models

# weight 
weight = {
    (25.0, "25 KG"),
    (26.0, "26 KG"),
    (50.0, "50 KG"),
}

unit_label = {
    ("Kg", "Kilogram"),
}


# Create your models here.
class Inventory(models.Model):
    business = models.ForeignKey('business.BusinessUser', on_delete=models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=100)
    weight = models.FloatField(choices=weight, default="25.0")
    unit_label = models.CharField(max_length=10, choices=unit_label, default="Kg")
    quantity = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"

    def __str__(self):
        
        return self.product_name
    
# sales log
class SalesLog(models.Model):
    business = models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    product = models.ForeignKey("Inventory", on_delete=models.CASCADE)
    weight = models.FloatField(choices=weight, null=True, blank=True)
    unit_label = models.CharField(max_length=10, choices=unit_label, null=True, blank=True)
    price = models.FloatField(default=0.0, null=False, blank=False)
    quantity_sold = models.IntegerField(null=False, blank=False)
    date = models.DateTimeField() 


    def __str__(self):
        return f"{self.product.product_name} - {self.quantity_sold} on {self.date}"
