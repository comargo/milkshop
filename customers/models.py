from django.db import models

from helpers import models as helpers_models


# Create your models here.
class Customer(helpers_models.Model):
    name = models.CharField(max_length=20, verbose_name='Имя', unique=True)

    class Meta:
        verbose_name = "Заказчик"

    def __str__(self):
        return self.name

    # def credits(self):
    #     for customer_order in self.orders.all():
    #         date = customer_order.order.date
    #         credit = sum()

    def transfers(self):
        _debits = ({'date': debit.date, 'debit': debit.amount, 'debit_obj': debit} for debit in self.debits.all())
        _credits = (
            {
                'date': customer_order.order.date,
                'credit': customer_order.order_cost()
            }
            for customer_order in self.orders.all() if customer_order.order_cost() != 0
        )
        from itertools import chain
        transfers = sorted(chain(_debits, _credits), key=lambda transfer: transfer['date'])
        return transfers

    def balance(self):
        return sum(
            (transfer.get('debit', 0) - transfer.get('credit', 0) for transfer in self.transfers())
        )


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
