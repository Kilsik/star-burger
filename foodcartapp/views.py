import json
import phonenumbers

from django.http import JsonResponse
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist
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

    order_kyes = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
    err_keys = []
    exist_key_error = False

    for key in order_kyes:
        if key not in data:
            err_keys.append(key)
            exist_key_error = True
    if exist_key_error:
        return Response({'error': f'Отсутствуют обязательные поля: {err_keys}'}, status=status.HTTP_204_NO_CONTENT)

    err_type = []
    exist_err_type =False

    for key in order_kyes[1:]:
        if not isinstance(data[key], str):
            err_type.append(key)
            exist_err_type = True
    if exist_err_type:
        return Response({'error': f'Несоответствие типа данных (не строка) в полях: {err_type}'}, status=status.HTTP_204_NO_CONTENT)

    err_data = []
    exist_data_error = False

    for key in order_kyes:
        if not data[key]:
            err_data.append(key)
            exist_data_error = True
    if exist_data_error:
        return Response({'error': f'Эти поля не могут быть пустыми: {err_data}'}, status=status.HTTP_204_NO_CONTENT)

    products = data['products']
    if not isinstance(products, list) or not products:
        return Response({'error': 'products не может быть нулевым или пустым списком'}, status=status.HTTP_204_NO_CONTENT)

    address = data['address']
    first_name = data['firstname']
    last_name = data['lastname']
    phone = PhoneNumber.from_string(data['phonenumber'], region='RU').as_e164
    phonenumber = phonenumbers.parse(phone, region='Russia')
    if not phonenumbers.is_valid_number(phonenumber):
        return Response({'error': 'phonenumber: введен некорректный номер телефона'}, status=status.HTTP_204_NO_CONTENT)

    order = Order.objects.create(
        address=address,
        name=first_name,
        surname=last_name,
        phone=phonenumber
    )
    for product in data['products']:
        product_id = product['product']
        quantity = product['quantity']
        try:
            order_product = Product.objects.get(pk=product_id)
        except ObjectDoesNotExist:
            return Response({'error': f'products: недопустимый первичный ключ {product_id}'}, status=status.HTTP_204_NO_CONTENT)
        possition = OrderProducts.objects.get_or_create(
            order=order,
            product=order_product,
            quantity=quantity,
        )
    print(data)
    return Response({})
