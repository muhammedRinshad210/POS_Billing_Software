from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name


# Create staff model here.
class Staff(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Create Supplier model here.
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.name


# Create sale models here.
class Sale(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    bill_number = models.CharField(max_length=50, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.bill_number


# Create saleitem models here.
class Saleitem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"






class Return(models.Model):
    sale_item = models.ForeignKey(Saleitem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return - {self.sale_item.product.name}"