from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse, reverse_lazy

from helpers.tests.views_helper import ViewTestCaseMixin
from orders import models, views, forms


class OrderViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_products', 'test_customers', 'test_orders']
    view_class = views.OrderView
    template_name = 'orders/order_detail.html'

    def setUp(self):
        super().setUp()
        self.order = models.Order.objects.first()

    def get_response(self):
        return self.client.get(self.order.get_absolute_url())

    def test_context_objects(self):
        response = self.get_response()
        self.assertEqual(self.order, response.context['object'])
        self.assertEqual(self.order, response.context['order'])
        self.assertEqual(
            [('customer', 'Заказчик'),
             ('1', 'type1 product1'),
             ('2', 'type1 product2'),
             ('3', 'type2 product3'),
             ('4', 'type2 product4')]
            , response.context['order_table_header'])
        self.assertEqual(
            [{'1': {'amount': 1, 'confirmed': None},
              '2': {'amount': None, 'confirmed': None},
              '3': {'amount': None, 'confirmed': None},
              '4': {'amount': 1, 'confirmed': None},
              'customer': 'user1'},
             {'1': {'amount': None, 'confirmed': None},
              '2': {'amount': 2, 'confirmed': None},
              '3': {'amount': 2, 'confirmed': None},
              '4': {'amount': None, 'confirmed': None},
              'customer': 'user2'}]
            , response.context['order_table'])
        self.assertEqual(
            {'customer': 'Итого',
             '1': {'amount': 1, 'confirmed': 0},
             '2': {'amount': 2, 'confirmed': 0},
             '3': {'amount': 2, 'confirmed': 0},
             '4': {'amount': 1, 'confirmed': 0}
             }, response.context['order_table_footer'])


class LastOrderViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_products', 'test_customers']
    view_class = views.LastOrderView
    template_name = 'orders/order_detail.html'
    url = reverse_lazy("orders:index")

    def get_response(self, use_fixtures=True):
        if use_fixtures:
            fixtures = ['test_orders']
            from django.core.management import call_command
            for fixture in fixtures:
                call_command('loaddata', fixture, verbosity=0)
        return self.client.get(self.url)

    def test_context_objects(self):
        response = self.get_response()
        order = models.Order.objects.latest()
        self.assertEqual(order, response.context['object'])
        self.assertEqual(order, response.context['order'])

    def test_no_latest(self):
        response = self.get_response(use_fixtures=False)
        self.assertRedirects(response, reverse('orders:create'))


class OrderCreateViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_products', 'test_customers']
    view_class = views.OrderCreateView
    template_name = 'orders/order_form.html'
    url = reverse_lazy("orders:create")

    @staticmethod
    def load_fixture():
        fixtures = ['test_orders']
        from django.core.management import call_command
        for fixture in fixtures:
            call_command('loaddata', fixture, verbosity=0)

    def get_response(self, use_fixtures=True):
        if use_fixtures:
            self.load_fixture()
        return self.client.get(self.url)

    def test_form(self):
        response = self.get_response()
        form = response.context['form']
        self.assertIsInstance(form, forms.OrderForm)
        self.assertEqual(['date'], [field.name for field in response.context['form'].visible_fields()])

    def test_initial(self):
        response = self.get_response()
        form = response.context['form']
        self.assertEqual({}, form.initial)
        self.assertEqual({
            'date': date(2001, 1, 14),
            'customers-0-customer': 1,
            'customers-0-product-1-1': 1,
            'customers-0-product-2-4': 1,
            'customers-1-customer': 2,
            'customers-1-product-1-2': 2,
            'customers-1-product-2-3': 2},
            response.context['post_initial']
        )

    def test_initial_new(self):
        response = self.get_response(use_fixtures=False)
        form = response.context['form']
        self.assertEqual({}, form.initial)
        self.assertEqual({'date': date.today() + timedelta(days=7)},
                         response.context['post_initial']
                         )

    def test_post_invalid(self):
        self.load_fixture()
        response = self.client.post(self.url, {'customers-TOTAL_FORMS': 3, 'customers-INITIAL_FORMS': 2})
        self.test_viewclass(response)
        self.test_status_code(response)
        self.test_template(response)
        self.assertFormError(response=response, form='form', field='date', errors='This field is required.')
        # alter context, to have formset in it
        response.context.append({'formset': response.context['form'].formset})
        self.assertFormsetError(response=response, formset="formset", form_index=0, field="customer",
                                errors='This field is required.')
        self.assertFormsetError(response=response, formset="formset", form_index=0, field="id",
                                errors='This field is required.')

    def test_post_valid(self):
        self.load_fixture()

        def order_translate(order):
            return {'pk': order.pk, 'date': order.date}

        def customer_order_translate(customer_order):
            return f''''pk': {customer_order.pk}, 'order.pk': {customer_order.order.pk}, 'customer.pk': {customer_order.customer.pk}'''

        def product_order_translate(product_order):
            return f''''pk': {product_order.pk}, 'customerOrder.pk': {product_order.customerOrder.pk}, 'product.pk': {product_order.product.pk}'''

        order_list = list(map(order_translate, models.Order.objects.all()))
        customer_order_list = list(map(customer_order_translate, models.CustomerOrder.objects.all()))
        product_order_list = list(map(product_order_translate, models.ProductOrder.objects.all()))
        response = self.client.post(self.url, {
            'date': date.today(),
            'customers-TOTAL_FORMS': 1,
            'customers-INITIAL_FORMS': 0,
            'customers-0-customer': 1,
            'customers-0-product-1-1': 1,
            'customers-0-product-2-4': 1,
        })
        new_order = models.Order.objects.get(date=date.today())
        order_list.append(order_translate(new_order))
        customer_order_list += list(map(customer_order_translate, new_order.customers.all()))
        product_order_list += list(map(
            product_order_translate,
            (product_order
             for customer_order in new_order.customers.all()
             for product_order in customer_order.product_orders.all()
             )
        ))
        self.assertQuerysetEqual(models.Order.objects.all(), order_list, order_translate)
        self.assertQuerysetEqual(models.CustomerOrder.objects.all(), customer_order_list,
                                 transform=customer_order_translate, ordered=False)
        self.assertQuerysetEqual(models.ProductOrder.objects.all(), product_order_list,
                                 transform=product_order_translate, ordered=False)
        self.assertRedirects(response=response, expected_url=new_order.get_absolute_url())


class OrderEditViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_products', 'test_customers', 'test_orders']
    view_class = views.OrderEditView
    template_name = 'orders/order_form.html'
    url = reverse_lazy("orders:create")

    def setUp(self):
        self.order = models.Order.objects.first()
        self.url = self.order.get_edit_url();

    def get_response(self):
        return self.client.get(self.url)

    def test_form(self):
        response = self.get_response()
        form = response.context['form']
        self.assertIsInstance(form, forms.OrderForm)
        self.assertEqual(['date'], [field.name for field in response.context['form'].visible_fields()])

    def test_context_objects(self):
        response = self.get_response()
        self.assertEqual(self.order, response.context['object'])
        self.assertEqual(self.order, response.context['order'])

    def test_initial(self):
        response = self.get_response()
        form = response.context['form']
        self.assertEqual({'date': date(2001, 1, 7)}, form.initial)
        self.assertEqual([{'customer': 1, 'order': 1, 'product-1-1': 1, 'product-2-4': 1},
                          {'customer': 2, 'order': 1, 'product-1-2': 2, 'product-2-3': 2},
                          {}],
                         [form.initial for form in form.formset])
        self.assertIsNone(response.context.get('post_initial'))

    def test_post_invalid(self):
        response = self.client.post(self.url, {'customers-TOTAL_FORMS': 1, 'customers-INITIAL_FORMS': 1})
        self.test_viewclass(response)
        self.test_status_code(response)
        self.test_template(response)
        self.assertFormError(response=response, form='form', field='date', errors='This field is required.')
        # alter context, to have formset in it
        response.context.append({'formset': response.context['form'].formset})
        self.assertFormsetError(response=response, formset="formset", form_index=0, field="customer",
                                errors='This field is required.')
        self.assertFormsetError(response=response, formset="formset", form_index=0, field="id",
                                errors='This field is required.')

    def test_post_valid(self):
        def order_translate(order):
            return {'pk': order.pk, 'date': order.date}

        def customer_order_translate(customer_order):
            return {'pk': customer_order.pk,
                    'order.pk': customer_order.order.pk,
                    'customer.pk': customer_order.customer.pk}

        def product_order_translate(product_order):
            return {'pk': product_order.pk,
                    'customerOrder.pk': product_order.customerOrder.pk,
                    'product.pk': product_order.product.pk}

        response = self.client.post(self.url, {
            'date': date.today(),
            'customers-TOTAL_FORMS': 2,
            'customers-INITIAL_FORMS': 2,
            'customers-0-customer': 1,
            'customers-0-id': 1,
            'customers-0-product-1-1': 1,
            'customers-0-product-2-4': 1,
            'customers-1-customer': 2,
            'customers-1-id': 2,
            'customers-1-product-1-1': 1,
            'customers-1-product-1-2': 1,
            'customers-1-product-2-3': 1,
            'customers-1-product-2-4': 1,
        })
        new_order = models.Order.objects.get(date=date.today())
        order_list = [order_translate(new_order)]
        self.assertQuerysetEqual(models.Order.objects.all(), order_list, order_translate)
        customer_order_list = [
            {'pk': 1, 'order.pk': 1, 'customer.pk': 1},
            {'pk': 2, 'order.pk': 1, 'customer.pk': 2}]
        self.assertQuerysetEqual(models.CustomerOrder.objects.all().order_by('pk'), customer_order_list,
                                 customer_order_translate)
        product_order_list = [
            {'pk': 1, 'customerOrder.pk': 1, 'product.pk': 1},
            {'pk': 2, 'customerOrder.pk': 1, 'product.pk': 4},
            {'pk': 3, 'customerOrder.pk': 2, 'product.pk': 2},
            {'pk': 4, 'customerOrder.pk': 2, 'product.pk': 3},
            {'pk': 5, 'customerOrder.pk': 2, 'product.pk': 1},
            {'pk': 6, 'customerOrder.pk': 2, 'product.pk': 4}]

        self.assertQuerysetEqual(models.ProductOrder.objects.all().order_by('pk'), product_order_list,
                                 product_order_translate)
        self.assertRedirects(response=response, expected_url=new_order.get_absolute_url())


class OrderConfirmViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_products', 'test_customers', 'test_orders']
    view_class = views.OrderConfirmView
    template_name = 'orders/order_confirm_form.html'

    def setUp(self):
        self.order = models.Order.objects.first()
        self.url = self.order.get_confirm_url();

    def get_response(self):
        return self.client.get(self.url)

    def test_form(self):
        response = self.get_response()
        form = response.context['form']
        self.assertIsInstance(form, forms.OrderForm)
        self.assertEqual([], [field.name for field in response.context['form'].visible_fields()])

    def test_context_objects(self):
        response = self.get_response()
        self.assertEqual(self.order, response.context['object'])
        self.assertEqual(self.order, response.context['order'])

    def test_initial(self):
        response = self.get_response()
        form = response.context['form']
        self.assertEqual({'date': date(2001, 1, 7)}, form.initial)
        self.assertEqual([{'customer': 1, 'order': 1, 'product-1-1': None, 'product-2-4': None},
                          {'customer': 2, 'order': 1, 'product-1-2': None, 'product-2-3': None}],
                         [form.initial for form in form.formset])
        self.assertEqual({'customers-0-product-1-1': 1,
                          'customers-0-product-2-4': 1,
                          'customers-1-product-1-2': 2,
                          'customers-1-product-2-3': 2},
                         response.context['post_initial'])

    def test_initial_second_confirm(self):
        self.order.customers.get(pk=1).product_orders.filter(pk=1).update(confirmed_amount=0)
        self.order.customers.get(pk=2).product_orders.update(confirmed_amount=1)
        for customer_order in self.order.customers.all():
            for product_order in customer_order.product_orders.all():
                product_order.confirmed_amount = 1 if product_order.product.product_type.pk != 1 else 0
                product_order.save()
        response = self.get_response()
        form = response.context['form']
        self.assertEqual({'date': date(2001, 1, 7)}, form.initial)
        self.assertEqual([{'customer': 1, 'order': 1, 'product-1-1': 0, 'product-2-4': None},
                          {'customer': 2, 'order': 1, 'product-1-2': 1, 'product-2-3': 1}],
                         [form.initial for form in form.formset])
        self.assertEqual({'customers-0-product-2-4': 1},
                         response.context['post_initial'])
