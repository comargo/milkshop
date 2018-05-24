from django.db import models
from helpers import models as helpers_models

# Create your models here.
from django.urls import reverse


class ProductType(helpers_models.Model):
    name = models.CharField(max_length=20, verbose_name="Тип продукции")

    class Meta:
        verbose_name = "Тип продукции"

    def __str__(self):
        return self.name


class Product(helpers_models.Model):
    product_type = models.ForeignKey(to=ProductType, on_delete=models.CASCADE, verbose_name="Тип продукции",
                                     related_name='products')
    name = models.CharField(max_length=20, verbose_name="Объем/особенность", blank=True)

    @property
    def price(self):
        try:
            return self.prices.latest().price
        except:
            return 0

    class Meta:
        verbose_name = "Продукция"

    def __str__(self):
        return "{self.product_type.name} {self.name}".format(self=self)

    def get_object_url_kwargs(self):
        kwargs: dict = self.product_type.get_object_url_kwargs()
        kwargs.update(super(Product, self).get_object_url_kwargs())
        return kwargs

    def get_absolute_url(self, kind=None):
        if kind is None:
            return self.product_type.get_absolute_url()
        else:
            return super().get_absolute_url(kind)


class Price(helpers_models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="Продукция", related_name="prices")
    price = models.PositiveIntegerField(verbose_name="Цена")
    date = models.DateField(verbose_name="Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Цена"
        get_latest_by = 'date'

    def __str__(self):
        return "{self.price}.00 ₽ ({self.date})".format(self = self)

    def get_object_url_kwargs(self):
        kwargs: dict = self.product.get_object_url_kwargs()
        kwargs.update(super(Price, self).get_object_url_kwargs())
        return kwargs

    def get_absolute_url(self, kind=None):
        if kind is None:
            return self.product.get_absolute_url()
        else:
            return super().get_absolute_url(kind)