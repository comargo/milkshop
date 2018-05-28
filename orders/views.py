from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import gettext as _
from django.views.generic import DetailView, CreateView, FormView, UpdateView
from django.views.generic.base import View, TemplateView

from orders import forms
from orders.models import Order
import products.models


# Create your views here.
class OrderMixin:
    model = Order
    pk_url_kwarg = 'order_pk'


class OrderView(OrderMixin, DetailView):
    def get_context_data(self, **kwargs):
        order = self.object
        order_table_header = [('customer', 'Заказчик')]
        order_table_header.extend(
            [(str(product.pk), str(product)) for product in products.models.Product.objects.all()]
        )

        order_table = []
        for customer in order.customers.all():
            customer_order = {'customer': str(customer.customer)}
            for product in products.models.Product.objects.all():
                try:
                    product_order = customer.product_orders.get(product=product)
                    amount = (product_order.amount or None, product_order.confirmed_amount or None)
                except customer.product_orders.model.DoesNotExist:
                    amount = (None, None)
                customer_order[str(product.pk)] = amount
            order_table.append(customer_order)
        order_table_footer = {'customer': 'Итого'}
        for product in products.models.Product.objects.all():
            order_table_footer[str(product.pk)] = (
                sum(customer_order[str(product.pk)][0] or 0 for customer_order in order_table),
                sum(customer_order[str(product.pk)][1] or 0 for customer_order in order_table),
            )

        context = {
            'order_table_header': order_table_header,
            'order_table': order_table,
            'order_table_footer': order_table_footer
        }
        context.update(kwargs)
        return super().get_context_data(**context)


class LastOrderView(OrderView):
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            obj = queryset.latest()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class OrderCreateView(OrderMixin, CreateView):
    form_class = forms.OrderForm


class OrderEditView(OrderMixin, UpdateView):
    form_class = forms.OrderForm


class OrderConfirmView(OrderMixin, UpdateView):
    form_class = forms.OrderConfirmForm
    template_name_suffix = '_confirm_form'
