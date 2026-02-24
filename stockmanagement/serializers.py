from rest_framework import serializers
from .models import *

class StokeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StokeItem
        fields = [
            "id",
            "name",
            "category",
            "quantity",
            "alert",
            "type",
            "nte_price",
            "total_price",
        ]


class StokeCategorySerializer(serializers.ModelSerializer):
    stokeitem = StokeItemSerializer(many=True, read_only=True)

    class Meta:
        model = StokeCategory
        fields = ["id", "name", "stokeitem"]
