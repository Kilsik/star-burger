from rest_framework import serializers
from phonenumber_field.modelfields import PhoneNumberField
from .models import Order, OrderProducts, Product


class OrderProductsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderProducts
        fields = [
            'product',
            'quantity',
        ]


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductsSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'address',
            'firstname',
            'lastname',
            'phonenumber',
            'products',
        ]

    def create(self, validated_data):
        order_products = validated_data.pop('products')
        order = Order.objects.create(validated_data)
        for order_product in order_products:
            cost = order_product['quantity'] * order_product['product'].price
            # product['cost'] = cost
            OrderProducts.objects.create(order=order,
                                         **order_product,
                                         cost=cost)
        
        return order