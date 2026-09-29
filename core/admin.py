from django.contrib import admin
from .models import Product,Staff,Supplier,Sale,Saleitem,Return

# Register your models here.
admin.site.register(Product)
admin.site.register(Staff)
admin.site.register(Supplier)
admin.site.register(Sale)
admin.site.register(Saleitem)
admin.site.register(Return)