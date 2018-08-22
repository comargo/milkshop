from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

import customers.models
import orders.models


class OrderTestCase(TestCase):
    fixtures = ['test_products', 'test_customers', 'test_orders']

    @staticmethod
    def _test_order():
        return orders.models.Order.objects.first()

    @staticmethod
    def _new_order():
        return orders.models.Order.objects.create(date=date.today())

    def test_order_cost_empty(self):
        test_order = self._new_order()
        self.assertEqual(0, test_order.order_cost())

    def test_order_cost(self):
        test_order = self._test_order()
        self.assertEqual(100 + 400 + 2 * 200 + 2 * 300, test_order.order_cost())

    def test_confirmed_cost_empty(self):
        test_order = self._new_order()
        self.assertEqual(0, test_order.confirmed_cost())

    def test_confirmed_cost_unconfirmed(self):
        test_order = self._test_order()
        self.assertEqual(0, test_order.confirmed_cost())

    def test_confirmed_cost(self):
        test_order = self._test_order()
        for test_customer_order in test_order.customers.all():
            for product_order in test_customer_order.product_orders.all():
                product_order.confirmed_amount = product_order.amount
                product_order.save()
        self.assertEqual(test_order.order_cost(), test_order.confirmed_cost())

    def test_get_urlpattern(self):
        test_order = self._test_order()
        self.assertEqual('orders:order', test_order.get_urlpattern())

    def test_get_object_url_kwargs(self):
        test_order = self._test_order()
        self.assertEqual({"order_pk": test_order.pk}, test_order.get_object_url_kwargs())

    def test_get_absolute_url(self):
        test_order = self._test_order()
        kwargs = {"order_pk": test_order.pk}
        self.assertEqual(reverse("orders:order", kwargs=kwargs),
                         test_order.get_absolute_url())
        self.assertEqual(reverse("orders:order-edit", kwargs=kwargs),
                         test_order.get_absolute_url("edit"))
        self.assertEqual(reverse("orders:order-delete", kwargs=kwargs),
                         test_order.get_absolute_url("delete"))

    def test_get_edit_url(self):
        test_order = self._test_order()
        self.assertEqual(reverse("orders:order-edit", kwargs={"order_pk": test_order.pk}),
                         test_order.get_edit_url())

    def test_get_delete_url(self):
        test_order = self._test_order()
        self.assertEqual(reverse("orders:order-delete", kwargs={"order_pk": test_order.pk}),
                         test_order.get_delete_url())


class CustomerOrderTestCase(TestCase):
    fixtures = ['test_products', 'test_customers', 'test_orders']

    @staticmethod
    def _test_customer_order():
        return orders.models.CustomerOrder.objects.first()

    @staticmethod
    def _new_customer_order():
        return OrderTestCase._new_order().customers.create(customer=customers.models.Customer.objects.first())

    def test_order_cost_empty(self):
        test_customer_order = self._new_customer_order()
        self.assertEqual(0, test_customer_order.order_cost())

    def test_order_cost(self):
        test_customer_order = self._test_customer_order()
        self.assertEqual(500, test_customer_order.order_cost())

    def test_confirmed_cost_empty(self):
        test_customer_order = self._new_customer_order()
        self.assertEqual(0, test_customer_order.confirmed_cost())

    def test_confirmed_cost_unconfirmed(self):
        test_customer_order = self._test_customer_order()
        self.assertEqual(0, test_customer_order.confirmed_cost())

    def test_confirmed_cost(self):
        test_customer_order = self._test_customer_order()
        for product_order in test_customer_order.product_orders.all():
            product_order.confirmed_amount = product_order.amount
            product_order.save()
        self.assertEqual(test_customer_order.order_cost(), test_customer_order.confirmed_cost())


class ProductOrderTestCase(TestCase):
    fixtures = ['test_products', 'test_customers', 'test_orders']

    @staticmethod
    def _test_product_order():
        return orders.models.ProductOrder.objects.first()

    def test_order_cost(self):
        test_product_order = self._test_product_order()
        self.assertEqual(100, test_product_order.order_cost())

    def test_confirmed_cost_unconfirmed(self):
        test_product_order = self._test_product_order()
        self.assertEqual(0, test_product_order.confirmed_cost())

    def test_confirmed_cost(self):
        test_product_order = self._test_product_order()
        test_product_order.confirmed_amount = test_product_order.amount
        self.assertEqual(test_product_order.order_cost(), test_product_order.confirmed_cost())

    def test_price_changed_in_order_date(self):
        test_product_order = self._test_product_order()
        price = test_product_order.product.prices.create(price=200)
        price.date = test_product_order.customerOrder.order.date
        price.save()
        test_product_order.confirmed_amount = test_product_order.amount
        test_product_order.save()
        self.assertEqual(200, test_product_order.order_cost())
        self.assertEqual(200, test_product_order.confirmed_cost())

    def test_price_changed_in_future(self):
        test_product_order = self._test_product_order()
        price = test_product_order.product.prices.create(price=200)
        price.date = test_product_order.customerOrder.order.date + timedelta(days=1)
        price.save()
        test_product_order.confirmed_amount = test_product_order.amount
        test_product_order.save()
        self.assertEqual(100, test_product_order.order_cost())
        self.assertEqual(100, test_product_order.confirmed_cost())
