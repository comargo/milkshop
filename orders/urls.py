from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView

import orders.views

app_name='orders'


order_urlpatterns = [
    path('', orders.views.OrderView.as_view(), name='order'),
    path('edit', orders.views.OrderEditView.as_view(), name='order-edit'),
    path('confirm', orders.views.OrderConfirmView.as_view(), name='order-confirm')
]


urlpatterns=[
    path('', orders.views.LastOrderView.as_view(), name='index'),
    path('create', orders.views.OrderCreateView.as_view(), name='create'),
    path('<int:order_pk>/', include(order_urlpatterns))
]