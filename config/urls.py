"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.login_view, name="login"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("billing/", views.billing, name="billing"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("invoice/<int:sale_id>/", views.invoice, name="invoice"),
    path("return/<int:sale_id>/", views.return_sale, name="return_sale"),
    path("transactions/", views.transactions, name="transactions"),
    path("reports/", views.reports, name="reports"),
    path("ledger/", views.ledger, name="ledger"),
    path("products/", views.products, name="products"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/edit/<int:product_id>/", views.edit_product, name="edit_product"),
    path("products/delete/<int:product_id>/", views.delete_product, name="delete_product"),
    path("staff/", views.staff_list, name="staff_list"),
    path("staff/add/", views.add_staff, name="add_staff"),
    path("staff/edit/<int:staff_id>/", views.edit_staff, name="edit_staff"),
    path("staff/delete/<int:staff_id>/", views.delete_staff, name="delete_staff"),
    path("suppliers/", views.suppliers, name="suppliers"),
    path("suppliers/add/", views.add_supplier, name="add_supplier"),
    path("suppliers/edit/<int:supplier_id>/", views.edit_supplier, name="edit_supplier"),
    path("suppliers/delete/<int:supplier_id>/", views.delete_supplier, name="delete_supplier"),
    path("returns/", views.returns_list, name="returns"),
    path("mobile-admin/", views.mobile_admin, name="mobile_admin"),
]
