from django import forms
import re

import orders.models
import products.models
import customers.models


class CustomerOrderForm(forms.Form):
    customer = forms.ModelChoiceField(queryset=customers.models.Customer.objects,
                                      label=customers.models.Customer._meta.verbose_name)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        order_fields = {}
        for product_type in products.models.ProductType.objects.all():
            for product in product_type.products.all():
                order_fields[f'product-{product_type.pk}-{product.pk}'] = forms.IntegerField(
                    label=str(product),
                    required=False)
        self.fields.update(order_fields)


OrderFormSet = forms.formset_factory(CustomerOrderForm)


class OrderForm(forms.ModelForm):
    class Meta:
        model = orders.models.Order
        fields = ['date', ]
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    formset = None
    amount_field = 'amount'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        formset_kwargs = kwargs.copy()
        if 'instance' in formset_kwargs:
            del formset_kwargs['instance']
        formset_kwargs['initial'] = self.get_formset_initial()
        self.formset = OrderFormSet(**formset_kwargs)

    def is_valid(self):
        return super().is_valid() and self.formset.is_valid()

    def save(self, commit=True):
        self.instance = super().save(commit)
        for subform_data in (x for x in self.formset.cleaned_data if len(x) > 0):
            self.save_subform(subform_data, self.amount_field)
        return self.instance

    def save_subform(self, data, amount_field = 'amount'):
        customerOrder, created = self.instance.customers.update_or_create(customer=data['customer'])
        customerOrder.save()
        pattern = r'product-(?P<type>\d+)-(?P<product>\d+)'
        for key, value in data.items():
            match = re.match(pattern, key)
            if not match:
                continue
            product = products.models.Product.objects.get(pk=match['product'], product_type=match['type'])
            if value and value > 0:
                product_order, created = customerOrder.product_orders.update_or_create(product=product,
                                                                                       defaults={amount_field: value})
                product_order.save()
            else:
                try:
                    product_order = customerOrder.product_orders.get(product=product)
                    setattr(product_order, amount_field, 0)
                    product_order.save()
                except customerOrder.product_orders.model.DoesNotExist:
                    pass

    def get_formset_initial(self):
        if 'formset' in self.initial:
            return self.initial['formset']
        if self.instance:
            initial = []
            for customerOrder in self.instance.customers.all():
                subform_initial = {'customer': customerOrder}
                for productOrder in customerOrder.product_orders.all():
                    product_key = f'product-{productOrder.product.product_type.pk}-{productOrder.product.pk}'
                    subform_initial[product_key] = productOrder.amount
                initial.append(subform_initial)
            return initial
        return None


class OrderConfirmForm(OrderForm):
    class Meta(OrderForm.Meta):
        widgets = {'date': forms.DateInput(attrs={'type': 'date', 'readonly': True})}
    amount_field = 'confirmed_amount'
