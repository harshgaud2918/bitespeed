from django.db import models

# Create your models here.


class Contact(models.Model):
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=256, null=True, blank=True)
    linked_id = models.IntegerField(default=None, null=True, blank=True)
    link_precedence = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=None, blank=True, null=True)
