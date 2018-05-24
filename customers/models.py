from django.db import models
from helpers import models as helpers_models

# Create your models here.
from django.urls import reverse


class Customer(helpers_models.Model):
    name = models.CharField(max_length=20, verbose_name='Имя', unique=True)
    class Meta:
        verbose_name="Заказчик"

    def __str__(self):
        return self.name

    def debit(self):
        return self.debits.aggregate(models.Sum('amount'))['amount__sum'] or 0

    def credit(self):
        return 0

    def balance(self):
        return self.debit()-self.credit()


class Debit(helpers_models.Model):
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE, verbose_name="Покупатель",
                                 related_name='debits')
    amount = models.IntegerField(verbose_name="Приход", default=0)
    date = models.DateField(verbose_name="Дата", auto_now_add=True)

    def get_object_url_kwargs(self):
        kwargs: dict = self.customer.get_object_url_kwargs()
        kwargs.update(super(Debit, self).get_object_url_kwargs())
        kwargs.update({'debit_date': self.date})
        return kwargs

    def get_absolute_url(self, kind=None):
        if kind is None:
            return self.customer.get_absolute_url()
        else:
            return super().get_absolute_url(kind)

