from datetime import date

from django.test import TestCase
from django.urls import NoReverseMatch

import customers.models


# Create your tests here.
class ModelTestCase(TestCase):
    fixtures = ['base']

    def test_customer_methods_initials(self):
        user: customers.models.Customer = customers.models.Customer.objects.all().first()
        self.assertEqual(user.name, str(user))
        self.assertEqual(user.balance(), 0)
        self.assertEqual(user.transfers(), [])
        self.assertEqual(user.get_urlpattern(), "customers:customer")
        self.assertEqual(user.get_object_url_kwargs(), {"customer_pk": user.pk})
        self.assertEqual(user.get_absolute_url(), f'/customers/{user.pk}/')
        self.assertRaises(NoReverseMatch, user.get_delete_url)
        self.assertEqual(user.get_edit_url(), f'/customers/{user.pk}/edit')

    def test_debit(self):
        user: customers.models.Customer = customers.models.Customer.objects.all().first()
        debit = user.debits.create(amount=100)
        self.assertEqual(user.balance(), 100)
        self.assertEqual(user.transfers(), [{'date': date.today(), 'debit': 100, 'debit_obj': debit}])

    def test_credit(self):
        user: customers.models.Customer = customers.models.Customer.objects.all().first()
#        product = customers.models.Customer.
