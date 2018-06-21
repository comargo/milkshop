from django.db import models

import products.models
# Create your models here.
from customers.models import Customer
from helpers import models as helpers_models


class Order(helpers_models.BrowseableObjectModel):
    date = models.DateField(verbose_name="Дата заказа")

    def order_cost(self):
        cost = 0
        for customer in self.customers.all():
            cost += customer.order_cost()
        return cost

    def get_confirm_url(self):
        return self.get_absolute_url('confirm')

    class Meta:
        get_latest_by = 'date'
        ordering = ['date']

    def __str__(self):
        return "Заказ {self.date:%Y-%m-%d}".format(self=self)


class CustomerOrder(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, verbose_name="Заказ", related_name="customers")
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE, verbose_name="Покупатель",
                                 related_name='orders')

    def __str__(self):
        return f"{self.order} for {self.customer}"

    def _cost(self, field):
        return sum((getattr(product_order, field)() for product_order in self.product_orders.all()))

    def confirmed_cost(self):
        return self._cost("confirmed_cost")

    def order_cost(self):
        return self._cost("order_cost")


class ProductOrder(models.Model):
    customerOrder = models.ForeignKey(to=CustomerOrder, on_delete=models.CASCADE, related_name='product_orders')
    product = models.ForeignKey(to=products.models.Product, on_delete=models.CASCADE,
                                verbose_name="Продукция", related_name='+')
    amount = models.PositiveSmallIntegerField(verbose_name="Количество")
    _confirmed_amount = models.PositiveSmallIntegerField(verbose_name="Подтвержденное количество", null=True)

    def __str__(self):
        return f"{self.customerOrder}:{self.product.name} ({self.amount}/{self._confirmed_amount})"

    def _price(self):
        query = self.product.prices.filter(date__lte=self.customerOrder.order.date)
        try:
            price_obj = query.latest()
        except products.models.Price.DoesNotExist:
            return 0
        return price_obj.price

    def order_cost(self):
        return self.amount * self._price()

    @property
    def confirmed_amount(self):
        return self._confirmed_amount or 0

    @confirmed_amount.setter
    def confirmed_amount(self, value):
        self._confirmed_amount = value

    def confirmed_cost(self):
        return self.confirmed_amount * self._price()
