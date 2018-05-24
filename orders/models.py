from django.db import models
from helpers import models as helpers_models

# Create your models here.
from customers.models import Customer
from products.models import Product, Price


class Order(helpers_models.Model):
    date = models.DateField(verbose_name="Дата заказа")

    def order_cost(self):
        cost = 0
        for customer in self.customers.all():
            cost += customer.order_cost()
        return cost

    class Meta:
        get_latest_by = 'date'

    def __str__(self):
        return "Заказ {self.date:%Y-%m-%d}".format(self=self)


class CustomerOrder(helpers_models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, verbose_name="Заказ", related_name="customers")
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE, verbose_name="Покупатель", related_name='+')

    def order_cost(self):
        cost = 0
        for product_order in self.product_orders.all():
            cost += product_order.order_cost()
        return cost

    def order_cost(self):
        cost = 0
        for product_order in self.product_orders.all():
            cost += product_order.order_cost()
        return cost


class ProductOrder(helpers_models.Model):
    customerOrder = models.ForeignKey(to=CustomerOrder, on_delete=models.CASCADE, related_name='product_orders')
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="Продукция", related_name='+')
    amount = models.PositiveSmallIntegerField(verbose_name="Количество")
    confirmed_amount = models.PositiveSmallIntegerField(verbose_name="Подтвержденное количество", default=0)

    def order_cost(self):
        return self.amount * self.price()

    def confirmed_cost(self):
        return self.confirmed_amount * self.price()

    def price(self):
        query = self.product.prices.filter(date__date__lte=self.customerOrder.order.date)
        try:
            price_obj = query.latest()
        except Price.DoesNotExist:
            return 0
        return price_obj.price
