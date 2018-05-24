import datetime

from django import forms

from products import models


class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = forms.ALL_FIELDS
        widgets = {
            'product_type': forms.HiddenInput
        }

    price = forms.IntegerField(label="Цена", widget=forms.NumberInput(attrs={'addon_after': '.00 &#8381;'}))
    price_date = forms.DateField(widget=forms.HiddenInput())

    def __init__(self, instance=None, initial=None, **kwargs):
        initial = initial or {}
        initial['price'] = 0
        initial['price_date'] = datetime.date.today()
        if instance:
            try:
                price_obj = instance.prices.latest()
                initial['price'] = price_obj.price
                initial['price_date'] = price_obj.date
            except models.Price.DoesNotExist:
                pass
        super(ProductForm, self).__init__(instance=instance, initial=initial, **kwargs)

    def save(self, commit=True):
        instance = super(ProductForm, self).save(commit)
        if 'price' in self.changed_data:
            instance.prices.update_or_create(date=self.initial['price_date'],
                                             defaults={'price': self.cleaned_data['price']}
                                             )
        return instance
