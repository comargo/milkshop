from django.urls import path, include

import orders.views

app_name = 'orders'

order_urlpatterns = [
    path('', orders.views.OrderView.as_view(), name='order'),
    path('edit', orders.views.OrderEditView.as_view(), name='order-edit'),
    path('confirm', orders.views.OrderConfirmView.as_view(), name='order-confirm'),
    path('delete', orders.views.OrderDeleteView.as_view(), name='order-delete')
]

urlpatterns = [
    path('', orders.views.LastOrderView.as_view(), name='index'),
    path('list', orders.views.OrdersListView.as_view(), name='list'),
    path('create', orders.views.OrderCreateView.as_view(), name='create'),
    path('<int:order_pk>/', include(order_urlpatterns))
]
