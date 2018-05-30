import django.forms
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, UpdateView, CreateView

import products.models
import products.forms
from helpers.views import CreateWithParentView


class ProductTypeMixin:
    model = products.models.ProductType
    pk_url_kwarg = 'producttype_pk'


class ProductMixin:
    model = products.models.Product
    pk_url_kwarg = 'product_pk'
    product_type = None

    def dispatch(self, request, *args, **kwargs):
        self.product_type = self.product_type or get_object_or_404(products.models.ProductType,
                                                                   pk=self.kwargs['producttype_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['product_type'] = self.product_type
        return super(ProductMixin, self).get_context_data(**kwargs)


class PriceMixin:
    model = products.models.Price
    pk_url_kwarg = 'price_pk'
    product = None

    def dispatch(self, request, *args, **kwargs):
        self.product = self.product or get_object_or_404(products.models.Product, pk=self.kwargs['product_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['product'] = self.product
        return super().get_context_data(**kwargs)


# Create your views here.
class ProductsListView(ProductTypeMixin, ListView):
    template_name = "products/product_list.html"


class ProductTypeEditView(ProductTypeMixin, UpdateView):
    fields = django.forms.ALL_FIELDS


class ProductTypeAddView(ProductTypeMixin, CreateView):
    fields = django.forms.ALL_FIELDS


class ProductEditView(ProductMixin, UpdateView):
    form_class = products.forms.ProductForm


class ProductAddView(ProductMixin, CreateWithParentView):
    form_class = products.forms.ProductForm
    parent_field = 'product_type'
