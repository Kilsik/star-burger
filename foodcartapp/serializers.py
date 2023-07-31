from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    order_datetime = serializers.DateTimeField()
    address = serializers.CharField(max_length=300)
    name = serializers.CharField(max_length=100)
    surname = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=12)
    products = serializers.ListField(child=serializers.DictField(child=serializers.ImageField()), min_length=1, write_only=True)
    
    def create(self, validated_data):
        return Order.objects.create(**validated_data)
