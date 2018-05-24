import django.forms
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView

import customers.forms
import customers.models
from helpers.views import CreateWithParentView


class CustomerMixin:
    model = customers.models.Customer
    pk_url_kwarg = 'customer_pk'


class DebitMixin:
    model = customers.models.Debit
    pk_url_kwarg = 'debit_pk'
    customer = None

    def get_queryset(self):
        qs = super(DebitMixin, self).get_queryset()
        qs = qs.filter(customer=self.customer)
        if 'debit_date' in self.kwargs and self.kwargs['debit_date']:
            qs = qs.filter(date=self.kwargs['debit_date'])
        return qs

    def dispatch(self, request, *args, **kwargs):
        self.customer = self.customer or get_object_or_404(customers.models.Customer, pk=self.kwargs['customer_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['customer'] = self.customer
        return super(DebitMixin, self).get_context_data(**kwargs)


# Create your views here.


class CustomersListView(CustomerMixin, ListView):
    pass


class CustomerDetailView(CustomerMixin, DetailView):
    pass


class CustomerCreateView(CustomerMixin, CreateView):
    fields = ['name', ]


class CustomerEditView(CustomerMixin, UpdateView):
    fields = ['name', ]


class DebitAddView(DebitMixin, CreateWithParentView):
    fields = ['amount', ]
    widgets = {
        'amount': django.forms.NumberInput(attrs={'addon_after': '.00 &#8381;'})
    }
    parent_field = 'customer'


class DebitEditView(DebitMixin, UpdateView):
    fields = ['amount', ]


class DebitView(DebitMixin, DetailView):
    pass


class DebitDeleteView(DebitMixin, DeleteView):
    def get_success_url(self):
        return self.customer.get_absolute_url()
