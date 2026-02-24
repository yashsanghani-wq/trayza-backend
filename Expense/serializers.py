from rest_framework import serializers
from .models import Expense, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = "__all__"

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

    def validate_payment_mode(self, value):
        valid_modes = [choice[0] for choice in Expense.PAYMENT_MODE_CHOICES]
        if value not in valid_modes:
            raise serializers.ValidationError("Invalid payment mode")
        return value