from rest_framework import serializers
from phonenumber_field.modelfields import PhoneNumberField
from .models import Order, OrderProducts, Product


class RestaurantSerializer():
    name = serializers.CharField()
    address = serializers.CharField()


class MenuItemSerializer(serializers.Serializer):
    restaurant = RestaurantSerializer()


class ProductSerializer(serializers.Serializer):
    menu_items = MenuItemSerializer()


class ProductDisplaySerializer(serializers.Serializer):
    quantity = serializers.IntegerField()
    cost = serializers.DecimalField(max_digits=8, decimal_places=2)
    product = ProductSerializer()


class OrderDisplaySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    phonenumber = serializers.CharField()
    address = serializers.CharField()
    status = serializers.CharField()
    payment = serializers.CharField()
    comment = serializers.CharField()
    products = ProductDisplaySerializer(many=True)

    class Meta:
        depth = 5


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
            'comment',
        ]
        
    def create(self, validated_data):
        order_products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for order_product in order_products:
            cost = order_product['quantity'] * order_product['product'].price
            OrderProducts.objects.create(order=order,
                                         **order_product,
                                         cost=cost)
        
        return order