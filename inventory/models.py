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