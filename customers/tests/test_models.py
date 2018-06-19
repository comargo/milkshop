from datetime import date, timedelta

from django.test import TestCase
from django.urls import NoReverseMatch, reverse

import customers.models
import orders.models
import products.models


# Create your tests here.
class CustomerTestCase(TestCase):
    fixtures = ['test_products']

    def _test_customer(self, name="test name", create_kwargs=None):
        create_kwargs = create_kwargs or {}
        test_customer = customers.models.Customer.objects.create(name=name, **create_kwargs)
        return test_customer

    def _test_debit(self, customer, amount=100, create_kwargs=None):
        create_kwargs = create_kwargs or {}
        test_debit = customer.debits.create(amount=amount, **create_kwargs)
        return test_debit

    def test___str__(self):
        test_customer = self._test_customer()
        self.assertIsInstance(test_customer, customers.models.Customer)
        self.assertEqual(str(test_customer), test_customer.name)

    def test_transfers_empty(self):
        test_customer = self._test_customer()
        self.assertEqual([], test_customer.transfers())

    def test_transfers_debit(self):
        test_customer = self._test_customer()
        amount = 100
        test_debit = self._test_debit(test_customer, amount=amount)
        self.assertEqual(
            [{'date': date.today(), 'debit': amount, 'debit_obj': test_debit}],
            test_customer.transfers()
        )

    def test_transfers_credit(self):
        test_customer = self._test_customer()
        product = products.models.Product.objects.first()
        order = orders.models.Order.objects.create(date=date.today())
        customer_order = order.customers.create(customer=test_customer)
        product_amount = 1
        customer_order.product_orders.create(product=product, amount=0, confirmed_amount=product_amount)
        self.assertEqual(
            [{'date': date.today(), 'credit': product.price * product_amount}],
            test_customer.transfers()
        )

    def test_transfers_debit_credit_ordering(self):
        test_customer = self._test_customer()
        debit_amount1 = 100
        debit_amount2 = 200
        test_debit1 = self._test_debit(test_customer, amount=debit_amount1)
        test_debit1.date = date.today() - timedelta(days=3)
        test_debit1.save()
        test_debit2 = self._test_debit(test_customer, amount=debit_amount2)
        product = products.models.Product.objects.first()

        product_amount1 = 1
        product_amount2 = 2
        orders.models.Order.objects.create(date=date.today() - timedelta(days=5)) \
            .customers.create(customer=test_customer) \
            .product_orders.create(product=product, amount=0, confirmed_amount=product_amount1)
        orders.models.Order.objects.create(date=date.today()) \
            .customers.create(customer=test_customer) \
            .product_orders.create(product=product, amount=0, confirmed_amount=product_amount2)

        self.assertEqual([
            {'date': date.today() - timedelta(days=5), 'credit': product.price * product_amount1},
            {'date': date.today() - timedelta(days=3), 'debit': debit_amount1, 'debit_obj': test_debit1},
            {'date': date.today(), 'debit': debit_amount2, 'debit_obj': test_debit2},
            {'date': date.today(), 'credit': product.price * product_amount2}
        ],
            test_customer.transfers()
        )

    def test_balance_init(self):
        test_customer = self._test_customer()
        self.assertEqual(0, test_customer.balance())

    def test_balance_debit(self):
        test_customer = self._test_customer()
        self.assertEqual(0, test_customer.balance())

        debits = [
            {'date': date.today() - timedelta(days=3), 'amount': 100},
            {'date': None, 'amount': 200}
        ]

        for test in range(len(debits)):
            with self.subTest(test):
                debit = debits[test]
                test_debit1 = self._test_debit(test_customer, amount=debit['amount'])
                if debit['date']:
                    test_debit1.date = date.today() - timedelta(days=3)
                    test_debit1.save()
                self.assertEqual(sum([debits[i]['amount'] for i in range(test + 1)]), test_customer.balance())

    def test_balance_credit(self):
        test_customer = self._test_customer()
        self.assertEqual(0, test_customer.balance())

        product = products.models.Product.objects.first()
        orders_info = [
            {'date': date.today() - timedelta(days=5), 'amount': 1},
            {'date': date.today() - timedelta(days=2), 'amount': 2},
            {'date': date.today(), 'amount': 3}
        ]

        for test in range(len(orders_info)):
            with self.subTest(test):
                order = orders_info[test]
                orders.models.Order.objects.create(date=order['date']) \
                    .customers.create(customer=test_customer) \
                    .product_orders.create(product=product, amount=0, confirmed_amount=order['amount'])

                self.assertEqual(-1 * sum(product.price * orders_info[i]['amount'] for i in range(test + 1)),
                                 test_customer.balance())

    def test_get_urlpattern(self):
        test_customer = self._test_customer()
        self.assertEqual('customers:customer', test_customer.get_urlpattern())

    def test_get_object_url_kwargs(self):
        test_customer = self._test_customer()
        self.assertEqual({"customer_pk": test_customer.pk}, test_customer.get_object_url_kwargs())

    def test_get_absolute_url(self):
        test_customer = self._test_customer()
        self.assertEqual(reverse("customers:customer", kwargs={"customer_pk": test_customer.pk}),
                         test_customer.get_absolute_url())
        self.assertEqual(reverse("customers:customer-edit", kwargs={"customer_pk": test_customer.pk}),
                         test_customer.get_absolute_url("edit"))
        self.assertEqual(reverse("customers:customer-debit", kwargs={"customer_pk": test_customer.pk}),
                         test_customer.get_absolute_url("debit"))
        self.assertRaisesMessage(NoReverseMatch, "customer-delete",
                                 test_customer.get_absolute_url, "delete")

    def test_get_edit_url(self):
        test_customer = self._test_customer()
        self.assertEqual(reverse("customers:customer-edit", kwargs={"customer_pk": test_customer.pk}),
                         test_customer.get_edit_url())

    def test_get_debit_url(self):
        test_customer = self._test_customer()
        self.assertEqual(reverse("customers:customer-debit", kwargs={"customer_pk": test_customer.pk}),
                         test_customer.get_debit_url())

    def test_get_delete_url(self):
        test_customer = self._test_customer()
        self.assertRaisesMessage(NoReverseMatch, "customer-delete", test_customer.get_delete_url)


class DebitTestCase(TestCase):
    def _test_customer(self, name="test name", create_kwargs=None):
        create_kwargs = create_kwargs or {}
        test_customer = customers.models.Customer.objects.create(name=name, **create_kwargs)
        return test_customer

    def _test_debit(self, customer=None, amount=100, create_kwargs=None):
        create_kwargs = create_kwargs or {}
        customer = customer or self._test_customer()
        test_debit = customer.debits.create(amount=amount, **create_kwargs)
        return test_debit

    def test_get_urlpattern(self):
        test_debit = self._test_debit()
        self.assertEqual('customers:debit', test_debit.get_urlpattern())

    def test_get_object_url_kwargs(self):
        test_debit = self._test_debit()
        self.assertEqual({"customer_pk": test_debit.customer.pk,
                          "debit_pk": test_debit.pk,
                          "debit_date": test_debit.date},
                         test_debit.get_object_url_kwargs())

    def test_get_absolute_url(self):
        test_debit = self._test_debit()
        self.assertEqual(reverse("customers:customer", kwargs=test_debit.customer.get_object_url_kwargs()),
                         test_debit.get_absolute_url())
        self.assertEqual(reverse("customers:debit-edit", kwargs=test_debit.get_object_url_kwargs()),
                         test_debit.get_absolute_url("edit"))
        self.assertEqual(reverse("customers:debit-delete", kwargs=test_debit.get_object_url_kwargs()),
                         test_debit.get_absolute_url("delete"))

    def test_get_edit_url(self):
        test_debit = self._test_debit()
        self.assertEqual(reverse("customers:debit-edit", kwargs=test_debit.get_object_url_kwargs()),
                         test_debit.get_edit_url())

    def test_get_delete_url(self):
        test_debit = self._test_debit()
        self.assertEqual(reverse("customers:debit-delete", kwargs=test_debit.get_object_url_kwargs()),
                         test_debit.get_delete_url())
