from datetime import date

from django.test import TestCase
from django.urls import reverse, reverse_lazy

from helpers.tests.views_helper import ViewTestCaseMixin
from products import views, models


class ProductsListViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_products']
    view_class = views.ProductsListView
    template_name = 'products/product_list.html'

    def get_response(self):
        return self.client.get(reverse('products:index'))

    def test_context_lists(self):
        response = self.get_response()
        self.assertQuerysetEqual(models.ProductType.objects.all(), map(repr, response.context['object_list']),
                                 ordered=False)
        self.assertQuerysetEqual(models.ProductType.objects.all(), map(repr, response.context['producttype_list']),
                                 ordered=False)


class ProductTypeEditViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_products']
    view_class = views.ProductTypeEditView
    template_name = 'products/producttype_form.html'

    def setUp(self):
        super().setUp()
        self.producttype = models.ProductType.objects.first()
        self.url = self.producttype.get_edit_url()

    def get_response(self):
        return self.client.get(self.url)

    def test_name_field(self):
        response = self.get_response()
        self.assertEqual(['name'], [field.name for field in response.context['form'].visible_fields()])
        self.assertEqual({'id': self.producttype.pk, 'name': self.producttype.name}, response.context['form'].initial)

    def test_post_invalid(self):
        response = self.client.post(self.url, {'name': ''})
        self.test_viewclass(response)
        self.test_status_code(response)
        self.test_template(response)
        self.assertFormError(response=response, form='form', field='name', errors='This field is required.')

    def test_post_valid(self):
        new_name = 'new type'
        response = self.client.post(self.url, {'name': new_name})
        new_producttype = models.ProductType.objects.get(pk=self.producttype.pk)
        self.assertEqual(new_producttype.name, new_name)
        self.assertRedirects(response, self.producttype.get_absolute_url(), target_status_code=301)


class ProductTypeAddViewTestCase(ViewTestCaseMixin, TestCase):
    view_class = views.ProductTypeAddView
    template_name = 'products/producttype_form.html'
    url = reverse_lazy('products:producttype-add')

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
        new_name = 'new type'
        response = self.client.post(self.url, {'name': new_name})
        new_producttype = models.ProductType.objects.get(name=new_name)
        self.assertRedirects(response, new_producttype.get_absolute_url(), target_status_code=301)


class ProductEditViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_products']
    view_class = views.ProductEditView
    template_name = 'products/product_form.html'

    def setUp(self):
        super().setUp()
        self.product = models.Product.objects.first()
        self.url = self.product.get_edit_url()

    def get_response(self):
        return self.client.get(self.url)

    def test_name_field(self):
        response = self.get_response()
        self.assertEqual(['name', 'price'], [field.name for field in response.context['form'].visible_fields()])
        self.assertEqual({
            'id': self.product.pk,
            'name': self.product.name,
            'product_type': self.product.product_type.pk,
            'price': self.product.prices.latest().price,
        }, response.context['form'].initial)

    def test_post_invalid(self):
        response = self.client.post(self.url, {'name': ''})
        self.test_viewclass(response)
        self.test_status_code(response)
        self.test_template(response)
        self.assertFormError(response=response, form='form', field='product_type', errors='This field is required.')
        self.assertFormError(response=response, form='form', field='price', errors='This field is required.')

    def test_post_valid(self):
        def price_transform(price: models.Price):
            return {'price': price.price, 'date': price.date}

        new_name = 'new product'
        new_price = 200
        prices = [price_transform(price) for price in self.product.prices.all()]
        prices.append({'price': new_price, 'date': date.today()})
        response = self.client.post(self.url,
                                    {'name': new_name,
                                     'product_type': self.product.product_type.pk,
                                     'price': new_price,
                                     })
        new_product = models.Product.objects.get(pk=self.product.pk)
        self.assertRedirects(response, self.product.get_absolute_url(), target_status_code=301)
        self.assertEqual(new_product.name, new_name)
        self.assertEqual(new_product.price, new_price)
        self.assertQuerysetEqual(new_product.prices.all(), prices, price_transform)


class ProductAddViewTestCase(ViewTestCaseMixin, TestCase):
    fixtures = ['test_products']
    view_class = views.ProductAddView
    template_name = 'products/product_form.html'

    def setUp(self):
        super().setUp()
        self.producttype = models.ProductType.objects.first()
        self.url = reverse('products:product-add', kwargs=self.producttype.get_object_url_kwargs())

    def get_response(self):
        return self.client.get(self.url)

    def test_name_field(self):
        response = self.get_response()
        self.assertEqual(['name', 'price'], [field.name for field in response.context['form'].visible_fields()])
        self.assertEqual({
            'product_type': self.producttype,
            'price': 0,
        }, response.context['form'].initial)

    def test_post_invalid(self):
        response = self.client.post(self.url, {'name': ''})
        self.test_viewclass(response)
        self.test_status_code(response)
        self.test_template(response)
        self.assertFormError(response=response, form='form', field='product_type', errors='This field is required.')
        self.assertFormError(response=response, form='form', field='price', errors='This field is required.')

    def test_post_valid(self):
        def price_transform(price: models.Price):
            return {'price': price.price, 'date': price.date}

        new_name = 'new product'
        new_price = 200
        prices = [{'price': new_price, 'date': date.today()}]
        response = self.client.post(self.url,
                                    {'name': new_name,
                                     'product_type': self.producttype.pk,
                                     'price': new_price,
                                     })
        new_product = models.Product.objects.get(name=new_name, product_type=self.producttype)
        self.assertRedirects(response, new_product.get_absolute_url(), target_status_code=301)
        self.assertEqual(new_product.name, new_name)
        self.assertEqual(new_product.price, new_price)
        self.assertQuerysetEqual(new_product.prices.all(), prices, price_transform)
