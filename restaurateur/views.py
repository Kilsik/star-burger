from django import forms
from django.db.models import Q, F, OuterRef, Subquery
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from foodcartapp.serializers import OrderSerializer, OrderDisplaySerializer
from geoposition.views import calc_distances


def get_restaurants(order):
    if order.prepared_by:
        return ''
    restaurants = Restaurant.objects.all()
    for product in order.products.all():
        menu_items = product.product.menu_items.values_list(F('restaurant_id'))
        restaurants = restaurants.filter(id__in=menu_items)
    return calc_distances(restaurants, order.address)

class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(
            restaurant.id, False
            ) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders_qset = Order.detail.fetch_cost().filter(~Q(status=Order.DONE)).prefetch_related('products')
    orders = []
    for order_qset in orders_qset:
        serializer = OrderDisplaySerializer(order_qset)
        # , data={
        #     'id': order_qset.pk,
        #     'status': order_qset.get_status_display(),
        #     'payment': order_qset.get_payment_display(),
        #     'prepared': order_qset.prepared_by,
        #     'restaurants': get_restaurants(order_qset),
        # })
        # serializer.is_valid()
        print(serializer.data)
        order = {}
        order['id'] = order_qset.pk
        order['client'] = f'{order_qset.firstname} {order_qset.lastname}'
        order['phone'] = order_qset.phonenumber
        order['address'] = order_qset.address
        order['cost'] = order_qset.order_cost
        order['status'] = order_qset.get_status_display()
        order['payment'] = order_qset.get_payment_display()
        order['comment'] = order_qset.comment
        if order_qset.prepared_by:
            order['prepared'] = order_qset.prepared_by
            order['restaurants'] = ''
        else:
            products = order_qset.products.all()
            restaurants = Restaurant.objects.all()
            for product in products:
                menu_items = product.product.menu_items.values_list(F('restaurant_id'))
                restaurants = restaurants.filter(id__in=menu_items)
            order['restaurants'] = calc_distances(restaurants, order['address'])
            order['prepared'] = ''
        orders.append(order)
    return render(request, template_name='order_items.html', context={
        'order_items': orders,
    })
