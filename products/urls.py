from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView

import products.views

app_name = 'products'
spec_urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('products:index'), permanent=True), name='product'),
    path('edit', products.views.ProductEditView.as_view(), name='product-edit')
]
product_urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('products:index'), permanent=True), name='producttype'),
    path('edit', products.views.ProductTypeEditView.as_view(), name='producttype-edit'),
    path('add', products.views.ProductAddView.as_view(), name='product-add'),
    path('<int:product_pk>/', include(spec_urlpatterns))
]
urlpatterns = [
    path('', products.views.ProductsListView.as_view(), name='index'),
    path('add', products.views.ProductTypeAddView.as_view(), name='producttype-add'),
    path('<int:producttype_pk>/', include(product_urlpatterns))
]
