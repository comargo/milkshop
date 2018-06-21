from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse, reverse_lazy

import orders.models
import products.models
from customers import models, views
from helpers.tests.views_helper import ViewTestCaseMixin


class CustomersListViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_customers']
    view_class = views.CustomersListView
    template_name = 'customers/customer_list.html'

    def get_response(self):
        return self.client.get(reverse('customers:index'))

    def test_context_lists(self):
        response = self.get_response()
        self.assertQuerysetEqual(models.Customer.objects.all(), map(repr, response.context['object_list']),
                                 ordered=False)
        self.assertQuerysetEqual(models.Customer.objects.all(), map(repr, response.context['customer_list']),
                                 ordered=False)


class CustomerDetailViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_customers']
    view_class = views.CustomerDetailView
    template_name = 'customers/customer_detail.html'

    def setUp(self):
        super().setUp()
        self.customer = models.Customer.objects.first()
        self._get_response = self.client.get(self.customer.get_absolute_url())

    def get_response(self):
        return self._get_response

    def test_context_objects(self):
        response = self.get_response()
        self.assertEqual(self.customer, response.context['object'])
        self.assertEqual(self.customer, response.context['customer'])


class CustomerCreateViewTestCase(ViewTestCaseMixin, TestCase):
    view_class = views.CustomerCreateView
    template_name = 'customers/customer_form.html'
    url = reverse_lazy('customers:create')

    def get_response(self):
        return self.client.get(self.url)

    def test_name_field(self):
        response = self.get_response()
        self.assertEqual(['name'], [field.name for field in response.context['form'].visible_fields()])
        self.assertEqual({}, response.context['form'].initial)

    def test_post_invalid(self):
        response = self.client.post(self.url, {'name': ''})
        self.test_viewclass(response)
        self.test_status_code(response)
        self.test_template(response)
        self.assertFormError(response=response, form='form', field='name', errors='This field is required.')

    def test_post_valid(self):
        new_name = 'new user'
        response = self.client.post(self.url, {'name': new_name})
        new_customer = models.Customer.objects.get(name=new_name)
        self.assertRedirects(response, new_customer.get_absolute_url())


class CustomerEditViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_customers']
    view_class = views.CustomerEditView
    template_name = 'customers/customer_form.html'

    def setUp(self):
        super().setUp()
        self.customer = models.Customer.objects.first()
        self.url = self.customer.get_edit_url()

    def get_response(self):
        return self.client.get(self.url)

    def test_name_field(self):
        response = self.get_response()
        self.assertEqual(['name'], [field.name for field in response.context['form'].visible_fields()])
        self.assertEqual({'name': self.customer.name}, response.context['form'].initial)

    def test_post_invalid(self):
        response = self.client.post(self.url, {'name': ''})
        self.test_viewclass(response)
        self.test_status_code(response)
        self.test_template(response)
        self.assertFormError(response=response, form='form', field='name', errors='This field is required.')

    def test_post_valid(self):
        new_name = 'new user'
        response = self.client.post(self.url, {'name': new_name})
        new_customer = models.Customer.objects.get(pk=self.customer.pk)
        self.assertEqual(new_customer.name, new_name)
        self.assertRedirects(response, self.customer.get_absolute_url())


class DebitAddViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_customers', 'test_products']
    view_class = views.DebitAddView
    template_name = 'customers/debit_form.html'

    def setUp(self):
        super().setUp()
        self.customer = models.Customer.objects.first()
        self.url = self.customer.get_debit_url()

    def get_response(self):
        return self.client.get(self.url)

    def test_amount_field_zero_balance(self):
        response = self.get_response()
        self.assertEqual(['amount'], [field.name for field in response.context['form'].visible_fields()])
        self.assertEqual({'customer': self.customer}, response.context['form'].initial)
        self.assertEqual({'addon_after': '.00 &#8381;'}, response.context['form'].fields['amount'].widget.attrs)

    def test_amount_field_negative_balance(self):
        product = products.models.Product.objects.first()
        orders.models.Order.objects.create(date=date.today()) \
            .customers.create(customer=self.customer) \
            .product_orders.create(product=product, amount=0, _confirmed_amount=1)

        response = self.get_response()
        self.assertEqual(['amount'], [field.name for field in response.context['form'].visible_fields()])
        self.assertEqual({'customer': self.customer, 'amount': self.customer.balance() * -1},
                         response.context['form'].initial)
        self.assertEqual({'addon_after': '.00 &#8381;'}, response.context['form'].fields['amount'].widget.attrs)

    def test_amount_field_positive_balance(self):
        self.customer.debits.create(amount=100)
        response = self.get_response()
        self.assertEqual(['amount'], [field.name for field in response.context['form'].visible_fields()])
        self.assertEqual({'customer': self.customer},
                         response.context['form'].initial)
        self.assertEqual({'addon_after': '.00 &#8381;'}, response.context['form'].fields['amount'].widget.attrs)

    def test_post_invalid(self):
        response = self.client.post(self.url, {'customer': self.customer.pk, 'amount': ''})
        self.test_viewclass(response)
        self.test_status_code(response)
        self.test_template(response)
        self.assertFormError(response=response, form='form', field='amount', errors='This field is required.')

    def test_post_valid(self):
        amount = 100
        response = self.client.post(self.url, {'customer': self.customer.pk, 'amount': amount})
        new_debit = self.customer.debits.first()
        self.assertEqual(amount, new_debit.amount)
        self.assertEqual(date.today(), new_debit.date)
        self.assertRedirects(response, new_debit.get_absolute_url())


class DebitEditViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_customers']
    view_class = views.DebitEditView
    template_name = 'customers/debit_form.html'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Customer.objects.first().debits.create(amount=100)

    def setUp(self):
        super().setUp()
        self.customer = models.Customer.objects.first()
        self.debit = self.customer.debits.first()
        self.url = self.debit.get_edit_url()

    def get_response(self):
        return self.client.get(self.url)

    def test_amount_field(self):
        response = self.get_response()
        self.assertEqual(['amount'], [field.name for field in response.context['form'].visible_fields()])
        self.assertEqual({'amount': self.debit.amount}, response.context['form'].initial)

    def test_post_invalid(self):
        response = self.client.post(self.url, {'amount': ''})
        self.test_viewclass(response)
        self.test_status_code(response)
        self.test_template(response)
        self.assertFormError(response=response, form='form', field='amount', errors='This field is required.')

    def test_post_valid(self):
        amount = 200
        response = self.client.post(self.url, {'amount': amount})
        new_debit = models.Debit.objects.get(pk=self.debit.pk)
        self.assertEqual(amount, new_debit.amount)
        self.assertRedirects(response, self.debit.get_absolute_url())


class DebitViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_customers']
    view_class = views.DebitView
    template_name = 'customers/debit_detail.html'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        debit = models.Customer.objects.first().debits.create(amount=100)
        debit.date -= timedelta(days=5)
        debit.save()
        models.Customer.objects.first().debits.create(amount=200)

    def setUp(self):
        super().setUp()
        self.customer = models.Customer.objects.first()
        self.debits = self.customer.debits.all()
        self.url = reverse(self.debits[0].get_urlpattern(), kwargs=self.debits[0].get_object_url_kwargs())

    def get_response(self):
        return self.client.get(self.url)

    def test_invalid_customer_id(self):
        kwargs = self.debits[0].get_object_url_kwargs()
        kwargs['customer_pk'] = models.Customer.objects.exclude(pk=self.customer.pk).first().pk
        url = reverse(self.debits[0].get_urlpattern(), kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_invalid_debit_date(self):
        kwargs = self.debits[0].get_object_url_kwargs()
        kwargs['debit_date'] = self.debits[1].date
        url = reverse(self.debits[0].get_urlpattern(), kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)


class DebitDeleteViewTestCase(ViewTestCaseMixin, TestCase):
    view_class = views.DebitDeleteView
    template_name = 'customers/debit_confirm_delete.html'
    fixtures = ['test_customers']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        debit = models.Customer.objects.first().debits.create(amount=100)
        debit.date -= timedelta(days=5)
        debit.save()
        models.Customer.objects.first().debits.create(amount=200)

    def setUp(self):
        super().setUp()
        self.customer = models.Customer.objects.first()
        self.debits = list(self.customer.debits.all())
        self.url = self.debits[0].get_delete_url()

    def get_response(self):
        return self.client.get(self.url)

    def test_confirm_delete(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, self.customer.get_absolute_url())
        self.assertQuerysetEqual(self.customer.debits.all(), [repr(self.debits[1])])
