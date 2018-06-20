from datetime import date, timedelta

from django.test import TestCase
from django.urls import NoReverseMatch, reverse

import products.models


class ProductTypeTestCase(TestCase):
    @staticmethod
    def _test_product_type(name="test type", create_kwargs=None):
        create_kwargs = create_kwargs or {}
        test_product_type = products.models.ProductType.objects.create(name=name, **create_kwargs)
        return test_product_type

    def test___str__(self):
        test_product_type = self._test_product_type()
        self.assertIsInstance(test_product_type, products.models.ProductType)
        self.assertEqual(str(test_product_type), test_product_type.name)

    def test_get_urlpattern(self):
        test_product_type = self._test_product_type()
        self.assertEqual('products:producttype', test_product_type.get_urlpattern())

    def test_get_object_url_kwargs(self):
        test_product_type = self._test_product_type()
        self.assertEqual({"producttype_pk": test_product_type.pk}, test_product_type.get_object_url_kwargs())

    def test_get_absolute_url(self):
        test_product_type = self._test_product_type()
        self.assertEqual(reverse("products:producttype", kwargs={"producttype_pk": test_product_type.pk}),
                         test_product_type.get_absolute_url())
        self.assertEqual(reverse("products:producttype-edit", kwargs={"producttype_pk": test_product_type.pk}),
                         test_product_type.get_absolute_url("edit"))
        self.assertRaisesMessage(NoReverseMatch, "producttype-delete", test_product_type.get_absolute_url, "delete")

    def test_get_edit_url(self):
        test_product_type = self._test_product_type()
        self.assertEqual(reverse("products:producttype-edit", kwargs={"producttype_pk": test_product_type.pk}),
                         test_product_type.get_edit_url())

    def test_get_delete_url(self):
        test_product_type = self._test_product_type()
        self.assertRaisesMessage(NoReverseMatch, "producttype-delete", test_product_type.get_delete_url)


class ProductTestCase(TestCase):
    @staticmethod
    def _test_product(name="test name", create_kwargs=None):
        create_kwargs = create_kwargs or {}
        test_product_type = ProductTypeTestCase._test_product_type()
        test_product = test_product_type.products.create(name=name, **create_kwargs)
        return test_product

    def test_price_initial(self):
        test_product = self._test_product()
        self.assertEqual(0, test_product.price)

    def test_price_some_added(self):
        test_product = self._test_product()
        price1 = test_product.prices.create(price=100)
        price1.date = date.today() - timedelta(days=5)
        price1.save()
        self.assertEqual(100, test_product.price)
        test_product.prices.create(price=200)
        self.assertEqual(200, test_product.price)
        price3 = test_product.prices.create(price=100)
        price3.date = date.today() + timedelta(days=5)
        price3.save()
        self.assertEqual(100, test_product.price)

    def test_get_urlpattern(self):
        test_product = self._test_product()
        self.assertEqual('products:product', test_product.get_urlpattern())

    def test_get_object_url_kwargs(self):
        test_product = self._test_product()
        self.assertEqual({"producttype_pk": test_product.product_type.pk, "product_pk": test_product.pk},
                         test_product.get_object_url_kwargs())

    def test_get_absolute_url(self):
        test_product = self._test_product()
        kwargs = {"producttype_pk": test_product.product_type.pk, "product_pk": test_product.pk}
        self.assertEqual(test_product.product_type.get_absolute_url(),
                         test_product.get_absolute_url())
        self.assertEqual(reverse("products:product-edit", kwargs=kwargs),
                         test_product.get_absolute_url("edit"))
        self.assertRaisesMessage(NoReverseMatch, "product-delete", test_product.get_absolute_url, "delete")

    def test_get_edit_url(self):
        test_product = self._test_product()
        self.assertEqual(reverse("products:product-edit", kwargs={"producttype_pk": test_product.product_type.pk,
                                                                  "product_pk": test_product.pk}),
                         test_product.get_edit_url())

    def test_get_delete_url(self):
        test_product = self._test_product()
        self.assertRaisesMessage(NoReverseMatch, "product-delete", test_product.get_delete_url)

    def test_get_field_name(self):
        test_product = self._test_product()
        self.assertEqual(f'product-{test_product.product_type.pk}-{test_product.pk}', test_product.get_field_name())
