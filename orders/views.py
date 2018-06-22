import datetime

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, CreateView, UpdateView

import products.models
from orders import forms
from orders.models import Order


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
                    amount = {'amount': product_order.amount or None,
                              'confirmed': product_order.confirmed_amount}
                except customer.product_orders.model.DoesNotExist:
                    amount = {'amount': None,
                              'confirmed': None}
                customer_order[str(product.pk)] = amount
            order_table.append(customer_order)
        order_table_footer = {'customer': 'Итого'}
        for product in products.models.Product.objects.all():
            order_table_footer[str(product.pk)] = {
                'amount': sum(customer_order[str(product.pk)]['amount'] or 0 for customer_order in order_table),
                'confirmed': sum(customer_order[str(product.pk)]['confirmed'] or 0 for customer_order in order_table),
            }

        context = {
            'order_table_header': order_table_header,
            'order_table': order_table,
            'order_table_footer': order_table_footer
        }
        context.update(kwargs)
        return super().get_context_data(**context)


class LastOrderView(OrderView):
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except self.model.DoesNotExist:
            return redirect(reverse('orders:create'))

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        obj = queryset.latest()
        return obj


class OrderCreateView(OrderMixin, CreateView):
    form_class = forms.OrderForm

    def get_context_data(self, form=None, **kwargs):
        orders = []
        order_date = datetime.date.today()
        try:
            latest_order = self.get_queryset().latest()
            for customer in latest_order.customers.all():
                order = {'customer': customer.customer.id}
                for product_order in customer.product_orders.all():
                    if product_order.amount:
                        order[product_order.product.get_field_name()] = product_order.amount
                orders.append(order)
            order_date = latest_order.date
        except Order.DoesNotExist:
            pass

        form = form or self.get_form()
        form.formset.extra = len(orders) + 1
        post_initial = {form.add_prefix('date'): order_date + datetime.timedelta(days=7)}
        for i in range(len(orders)):
            for field, value in orders[i].items():
                post_initial[form.formset[i].add_prefix(field)] = value
        return super().get_context_data(post_initial=post_initial, form=form, **kwargs)


class OrderEditView(OrderMixin, UpdateView):
    form_class = forms.OrderForm


class OrderConfirmView(OrderMixin, UpdateView):
    form_class = forms.OrderConfirmForm
    template_name_suffix = '_confirm_form'

    def get_context_data(self, form=None, **kwargs):
        form = form or self.get_form()
        post_initial = {}
        #        for fields in form.visible_fields():
        #            post_initial[]
        for subform in form.formset.forms:
            customer = self.object.customers.get(customer_id=subform['customer'].value())
            for product_order in customer.product_orders.all():
                if product_order.amount and product_order.confirmed_amount is None:
                    post_initial[subform.add_prefix(product_order.product.get_field_name())] = product_order.amount
        return super().get_context_data(post_initial=post_initial, form=form, **kwargs)
