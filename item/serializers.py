from rest_framework import serializers
from .models import *

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "category", "base_cost", "selection_rate"]

class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'item', 'ingredients', 'person_count']


class IngredientCalcSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False
    )
    persons = serializers.IntegerField(min_value=1)


class EditRecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredients', 'person_count']
