import json

from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .models import Product, Order, OrderProducts


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    try:
        data = request.data
    except ValueError as err:
        print(f'Произошла ошибка {err}')
    try:
        products = data['products']
    except KeyError:
        return Response({'error': 'products: Обязательное поле'}, status=status.HTTP_204_NO_CONTENT)
    if not isinstance(products, list) or not products:
        return Response({'error': 'products должен быть ненулевым или пустым списком'}, status=status.HTTP_204_NO_CONTENT)
    address = data['address']
    first_name = data['firstname']
    last_name = data['lastname']
    phone = PhoneNumber.from_string(data['phonenumber'])
    order = Order.objects.create(
        address=address,
        name=first_name,
        surname=last_name,
        phone=phone
    )
    for product in data['products']:
        product_id = product['product']
        quantity = product['quantity']
        order_product = Product.objects.get(pk=product_id)
        possition = OrderProducts.objects.get_or_create(
            order=order,
            product=order_product,
            quantity=quantity,
        )
    print(data)
    return Response({})
