from django.db import models

# Create your models here.
class IngridientsCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    positions = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    

class IngridientsItem(models.Model):
    category = models.ForeignKey(
        IngridientsCategory, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name
    
class EventIngridientList(models.Model):
    event_id = models.CharField(max_length=100, unique=True)
    ingridient_list_data = models.JSONField(default=dict)