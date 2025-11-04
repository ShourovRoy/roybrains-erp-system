from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class BusinessUser(AbstractUser):
    business_name = models.CharField(max_length=255)
    business_address = models.TextField()
    contact_number = models.CharField(max_length=15, unique=True)
    owner_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'business_name', 'contact_number', 'owner_name']

    def save(self, **kwargs):
        self.username = self.email + self.owner_name

        super().save(**kwargs)

    def __str__(self):
        return self.business_name