# import json
import phonenumbers

from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
# from django.core.exceptions import ObjectDoesNotExist
# from phonenumber_field.phonenumber import PhoneNumber
# from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
# from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .models import Product, Order, OrderProducts
from .serializers import OrderSerializer


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


def order_validation(data):
    errors = []

    order_kyes = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
    err_keys = []
    exist_key_error = False

    for key in order_kyes:
        if key not in data:
            err_keys.append(key)
            exist_key_error = True
    if exist_key_error:
        errors.append({'error': f'Отсутствуют обязательные поля: {err_keys}'})

    err_type = []
    exist_err_type =False

    for key in order_kyes[1:]:
        if not isinstance(data[key], str):
            err_type.append(key)
            exist_err_type = True
    if exist_err_type:
        errors.append({'error': f'Несоответствие типа данных (не строка) в полях: {err_type}'})

    products = data['products']
    if not isinstance(products, list) or not products:
        errors.append({'error': 'products не может быть нулевым или пустым списком'})

    err_data = []
    exist_data_error = False

    for key in order_kyes:
        if not data[key]:
            err_data.append(key)
            exist_data_error = True
    if exist_data_error:
        errors.append({'error': f'Эти поля не могут быть пустыми: {err_data}'})

    for product in data['products']:
        product_id = product['product']
        if product_id not in list(Product.objects.all().values_list('id', flat=True)):
            errors.append({'error': f'products: недопустимый первичный ключ {product_id}'})
    if not phonenumbers.is_valid_number(phonenumbers.parse(data['phonenumber'], region='Russia')):
        errors.append({'error': 'phonenumber: введен некорректный номер телефона'})
    
    if errors:
        raise ValidationError(errors)


@api_view(['POST'])
def register_order(request):
    try:
        data = request.data
    except ValueError as err:
        raise ValidationError(f'Произошла ошибка {err}')

    order_validation(data)
    address = data['address']
    first_name = data['firstname']
    last_name = data['lastname']
    phonenumber = phonenumbers.parse(data['phonenumber'], region='Russia')

    with transaction.atomic():
        order = Order.detail.create(
            address=address,
            name=first_name,
            surname=last_name,
            phone=phonenumber
        )
        serializer = OrderSerializer(order)
        for product in data['products']:
            product_id = product['product']
            quantity = product['quantity']
            order_product = Product.objects.get(pk=product_id)
            OrderProducts.objects.get_or_create(
                order=order,
                product=order_product,
                quantity=quantity,
                cost=order_product.price * quantity,
            )
    # content = JSONRenderer().render(serializer.data)
    return Response(serializer.data)
