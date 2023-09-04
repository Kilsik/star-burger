from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField


class OrderManager(models.QuerySet):
    def fetch_cost(self):
        return self.annotate(order_cost=Sum(F('products__cost')))


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
        db_index=True,
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=250,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    NEW = 'NEW'
    PREPARE = 'PRE'
    DELIVER = 'DLV'
    DONE = 'DONE'
    STATUS_CHOICE = [
        (NEW, 'Необработан'),
        (PREPARE, 'Готовится'),
        (DELIVER, 'Доставляется'),
        (DONE, 'Доставлен'),
    ]
    ELECTRONIC = 'EL'
    CASH = 'CASH'
    PAYMENT = [
        (ELECTRONIC, 'Электронно'),
        (CASH, 'Наличностью'),
    ]
    status = models.CharField(
        max_length=4,
        choices=STATUS_CHOICE,
        verbose_name='Статус',
        db_index=True,
    )
    payment = models.CharField(
        max_length=4,
        choices=PAYMENT,
        verbose_name='Способ оплаты',
        default=CASH,
        db_index=True,
    )
    registrated_at = models.DateTimeField(
        'дата и время поступления заказа',
        db_index=True,
        default=timezone.now()
    )
    called_ad = models.DateTimeField(
        'дата и время звонка',
        blank=True,
        null=True,
    )
    delivered_at = models.DateTimeField(
        'дата и время доставки',
        blank=True,
        null=True,
    )
    address = models.CharField(
        'адрес',
        max_length=300,
        db_index=True,
    )
    name = models.CharField(
        'имя',
        max_length=100,
    )
    surname = models.CharField(
        'фамилия',
        max_length=200,
        blank=True,
    )
    phone = PhoneNumberField(
        'телефон',
        region='RU',
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        null=True,
    )
    prepared_by = models.ForeignKey(
        Restaurant,
        verbose_name='Готовит',
        related_name='orders',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    objects = models.Manager()
    detail = OrderManager.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        indexes = [
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return f'{self.name} {self.surname} - {self.address}'


class OrderProducts(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='заказ',
        on_delete=models.CASCADE,
        related_name='products',
    )
    product = models.ForeignKey(
        Product,
        verbose_name='пункт заказа',
        related_name='orders',
        on_delete=models.DO_NOTHING,
    )
    quantity = models.PositiveIntegerField(
        'количество',
    )
    cost = models.DecimalField(
        verbose_name='Сумма по позиции заказа',
        max_digits=8,
        decimal_places=2,
    )
    
    class Meta:
        verbose_name = 'пункт заказа'
        verbose_name_plural = 'пункты заказа'
