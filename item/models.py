from django.db import models
from category.models import Category

class Item(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=200, unique=True)
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selection_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    item = models.OneToOneField(Item, related_name="recipe", on_delete=models.CASCADE)
    ingredients = models.JSONField(default=dict)
    person_count = models.IntegerField(default=100)

    def __str__(self):
        return f"Ingredients for {self.item.name} ({self.person_count} persons)"
