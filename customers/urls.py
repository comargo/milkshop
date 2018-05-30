from django.urls import path, include

import customers.views

app_name = 'customers'

debit_urlpatterns = [
    path('', customers.views.DebitView.as_view(), name='debit'),
    path('edit', customers.views.DebitEditView.as_view(), name='debit-edit'),
    path('delete', customers.views.DebitDeleteView.as_view(), name='debit-delete')

]

customer_urlpatterns = [
    path('', customers.views.CustomerDetailView.as_view(), name='customer'),
    path('edit', customers.views.CustomerEditView.as_view(), name='customer-edit'),
    path('debit', customers.views.DebitAddView.as_view(), name='debit-add'),
    path('debit/<date:debit_date>-<int:debit_pk>/', include(debit_urlpatterns)),
]
urlpatterns = [
    path('', customers.views.CustomersListView.as_view(), name='index'),
    path('create', customers.views.CustomerCreateView.as_view(), name='create'),
    path('<int:customer_pk>/', include(customer_urlpatterns))
]
