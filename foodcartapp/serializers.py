from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'registrated_at',
            'address',
            'name',
            'surname',
            'phone',
        ]