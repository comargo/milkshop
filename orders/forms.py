from django import forms
import re

import orders.models
import products.models
import customers.models


class CustomerOrderForm(forms.ModelForm):
    class Meta:
        model = orders.models.CustomerOrder
        fields = ['customer']

    amount_field = 'amount'

    def __init__(self, amount_field=None, **kwargs):
        super().__init__(**kwargs)
        order_fields = {}
        for product_type in products.models.ProductType.objects.all():
            for product in product_type.products.all():
                order_fields[product.get_field_name()] = forms.IntegerField(
                    label=str(product),
                    required=False)
        self.fields.update(order_fields)
        self.amount_field = amount_field or self.amount_field
        self.initial.update(self.get_initial())

    def get_initial(self):
        if self.instance:
            initial = {}
            for product_order in self.instance.product_orders.all():
                initial[product_order.product.get_field_name()] = getattr(product_order, self.amount_field)
            return initial
        return None

    def _save_m2m(self):
        pattern = r'product-(?P<type>\d+)-(?P<product>\d+)'
        for key, value in self.cleaned_data.items():
            match = re.match(pattern, key)
            if not match:
                continue
            product = products.models.Product.objects.get(pk=match['product'], product_type=match['type'])
            if value and value > 0:
                product_order, created = self.instance.product_orders.update_or_create(product=product,
                                                                                  defaults={self.amount_field: value})
                product_order.save()
            else:
                try:
                    product_order = self.instance.product_orders.get(product=product)
                    setattr(product_order, self.amount_field, 0)
                    product_order.save()
                except self.instance.product_orders.model.DoesNotExist:
                    pass
        return self.instance



OrderFormSet = forms.inlineformset_factory(orders.models.Order, orders.models.CustomerOrder, form=CustomerOrderForm,
                                           extra=1, can_delete=False)


class CustomerOrderConfirmForm(CustomerOrderForm):
    class Meta(CustomerOrderForm.Meta):
        widgets = {'customer': forms.HiddenInput}

    amount_field = 'confirmed_amount'

    def get_initial(self):
        if self.instance:
            initial = {}
            for product_order in self.instance.product_orders.all():
                initial[product_order.product.get_field_name()] = product_order.confirmed_amount or None
            return initial
        return None


OrderConfirmFormSet = forms.inlineformset_factory(orders.models.Order, orders.models.CustomerOrder,
                                                  form=CustomerOrderConfirmForm, extra=0, can_delete=False)


class OrderForm(forms.ModelForm):
    class Meta:
        model = orders.models.Order
        fields = ['date', ]
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    formset = None
    formset_class = OrderFormSet

    def __init__(self, initial=None, **kwargs):
        super().__init__(initial=initial, **kwargs)
        self.formset = self.get_formset_class()(initial=(initial or {}).get('order', None), **kwargs)

    def get_formset_class(self):
        return self.formset_class

    def is_valid(self):
        return super().is_valid() and self.formset.is_valid()

    def save(self, commit=True):
        self.formset.instance = super().save(commit)
        self.formset.save(commit)
        return self.instance


class OrderConfirmForm(OrderForm):
    class Meta(OrderForm.Meta):
        widgets = {'date': forms.HiddenInput}

    formset_class = OrderConfirmFormSet
