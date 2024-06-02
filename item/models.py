from django.contrib.auth.models import User
from django.core.validators import BaseValidator
from django.db import models


class MinValueValidator(BaseValidator):
    message = 'Ensure this value is greater than or equal to %(limit_value)s.'
    code = 'min_value'

    def compare(self, a, b):
        return a < b


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    image = models.ImageField(upload_to='item_images', blank=True, null=True)
    quantity = models.IntegerField(default=0, null=False, validators=[MinValueValidator(0)])
    updated_at = models.DateTimeField(auto_now_add=True)
    is_with_prescription = models.BooleanField(default=False)

    def __str__(self):
        return self.name
