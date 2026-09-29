from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Product, Staff, Sale, Saleitem, Return, Supplier
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.db import models


# Create your views here.
from django.contrib import messages

def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect("admin_dashboard")
            else:
                return redirect("billing")

        messages.error(request, "Invalid username or password.")

    return render(request, "core/login.html")




# dashboard
@login_required
def dashboard(request):
    return render(request, "core/dashboard.html")




# admin dashboard
@login_required
def admin_dashboard(request):
    return render(request, "core/admin_dashboard.html")




# billing
@login_required
def billing(request):
    products = Product.objects.all()

    return render(request, "core/billing.html",
                  {"products": products})



# add to cart
def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session["cart"] = cart

    return redirect("billing")




# cart display
@login_required
def cart(request):
    cart_data = request.session.get("cart", {})

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():
        product = Product.objects.get(id=product_id)

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    return render(
        request,
        "core/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )




# check out view
@login_required
def checkout(request):
    cart_data = request.session.get("cart", {})

    if not cart_data:
        return redirect("billing")

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():
        product = Product.objects.get(id=product_id)

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        staff = Staff.objects.get(
            email=request.user.email
        )

        with transaction.atomic():

            sale = Sale.objects.create(
                staff=staff,
                bill_number=f"INV-{Sale.objects.count() + 1:04d}",
                total=total,
                payment_method=payment_method,
            )

            for item in cart_items:

                Saleitem.objects.create(
                    sale=sale,
                    product=item["product"],
                    quantity=item["quantity"],
                    price=item["product"].price,
                )

                product = item["product"]
                product.stock -= item["quantity"]
                product.save()

            request.session["cart"] = {}

        return redirect("invoice", sale_id=sale.id)

    return render(
        request,
        "core/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )





@login_required
def invoice(request, sale_id):
    sale = Sale.objects.get(id=sale_id)

    items = Saleitem.objects.filter(sale=sale)

    for item in items:
        item.subtotal = item.price * item.quantity

    return render(
        request,
        "core/invoice.html",
        {
            "sale": sale,
            "items": items,
        }
    )





@login_required
def return_sale(request, sale_id):
    sale = Sale.objects.get(id=sale_id)

    items = Saleitem.objects.filter(sale=sale)

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantity = int(request.POST.get("quantity"))
        reason = request.POST.get("reason")

        item = Saleitem.objects.get(id=item_id)

        # Already returned quantity
        returned_quantity = Return.objects.filter(
            sale_item=item
        ).aggregate(
            total=models.Sum("quantity")
        )["total"] or 0

        # Remaining quantity available for return
        remaining_quantity = item.quantity - returned_quantity

        if quantity <= 0:
            return render(
                request,
                "core/return.html",
                {
                    "sale": sale,
                    "items": items,
                    "error": "Return quantity must be greater than 0.",
                }
            )

        if quantity > remaining_quantity:
            return render(
                request,
                "core/return.html",
                {
                    "sale": sale,
                    "items": items,
                    "error": f"Only {remaining_quantity} item(s) can be returned.",
                }
            )

        Return.objects.create(
            sale_item=item,
            quantity=quantity,
            reason=reason,
        )

        # Restore product stock
        product = item.product
        product.stock += quantity
        product.save()

        return redirect(
            "invoice",
            sale_id=sale.id
        )

    return render(
        request,
        "core/return.html",
        {
            "sale": sale,
            "items": items,
        }
    )






@login_required
def transactions(request):
    sales = Sale.objects.select_related("staff").order_by("-date")

    return render(
        request,
        "core/transactions.html",
        {
            "sales": sales,
        }
    )





@login_required
def reports(request):

    now = timezone.now()

    today = now.date()

    week_start = today - timedelta(days=7)

    month_start = today.replace(day=1)

    today_sales = Sale.objects.filter(
        date__date=today
    ).aggregate(
        total=Sum("total")
    )["total"] or 0

    week_sales = Sale.objects.filter(
        date__date__gte=week_start
    ).aggregate(
        total=Sum("total")
    )["total"] or 0

    month_sales = Sale.objects.filter(
        date__date__gte=month_start
    ).aggregate(
        total=Sum("total")
    )["total"] or 0

    transaction_count = Sale.objects.count()

    return render(
        request,
        "core/reports.html",
        {
            "today_sales": today_sales,
            "week_sales": week_sales,
            "month_sales": month_sales,
            "transaction_count": transaction_count,
        }
    )






@login_required
def ledger(request):
    sales = Sale.objects.select_related("staff").order_by("-date")

    total_amount = sales.aggregate(
        total=Sum("total")
    )["total"] or 0

    return render(
        request,
        "core/ledger.html",
        {
            "sales": sales,
            "total_amount": total_amount,
        }
    )







@login_required
def products(request):
    products = Product.objects.all().order_by("name")

    return render(
        request,
        "core/products.html",
        {"products": products}
    )


@login_required
def add_product(request):

    if request.method == "POST":

        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock")

        Product.objects.create(
            name=name,
            price=price,
            stock=stock
        )

        return redirect("products")

    return render(request, "core/add_product.html")


@login_required
def edit_product(request, product_id):

    product = Product.objects.get(id=product_id)

    if request.method == "POST":

        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")

        product.save()

        return redirect("products")

    return render(
        request,
        "core/edit_product.html",
        {"product": product}
    )


@login_required
def delete_product(request, product_id):

    product = Product.objects.get(id=product_id)

    if request.method == "POST":
        product.delete()
        return redirect("products")

    return render(
        request,
        "core/delete_product.html",
        {"product": product}
    )





@login_required
def staff_list(request):
    staff_members = Staff.objects.all().order_by("name")

    return render(
        request,
        "core/staff.html",
        {"staff_members": staff_members}
    )


@login_required
def add_staff(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        role = request.POST.get("role")

        Staff.objects.create(
            name=name,
            email=email,
            role=role
        )

        return redirect("staff_list")

    return render(request, "core/add_staff.html")


@login_required
def edit_staff(request, staff_id):

    staff = Staff.objects.get(id=staff_id)

    if request.method == "POST":

        staff.name = request.POST.get("name")
        staff.email = request.POST.get("email")
        staff.role = request.POST.get("role")

        staff.save()

        return redirect("staff_list")

    return render(
        request,
        "core/edit_staff.html",
        {"staff": staff}
    )


@login_required
def delete_staff(request, staff_id):

    staff = Staff.objects.get(id=staff_id)

    if request.method == "POST":
        staff.delete()
        return redirect("staff_list")

    return render(
        request,
        "core/delete_staff.html",
        {"staff": staff}
    )




@login_required
def suppliers(request):
    suppliers = Supplier.objects.all().order_by("name")

    return render(
        request,
        "core/suppliers.html",
        {"suppliers": suppliers}
    )


@login_required
def add_supplier(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        Supplier.objects.create(
            name=name,
            phone=phone,
            address=address
        )

        return redirect("suppliers")

    return render(request, "core/add_supplier.html")


@login_required
def edit_supplier(request, supplier_id):
    supplier = Supplier.objects.get(id=supplier_id)

    if request.method == "POST":
        supplier.name = request.POST.get("name")
        supplier.phone = request.POST.get("phone")
        supplier.address = request.POST.get("address")

        supplier.save()

        return redirect("suppliers")

    return render(
        request,
        "core/edit_supplier.html",
        {"supplier": supplier}
    )


@login_required
def delete_supplier(request, supplier_id):
    supplier = Supplier.objects.get(id=supplier_id)

    if request.method == "POST":
        supplier.delete()

        return redirect("suppliers")

    return render(
        request,
        "core/delete_supplier.html",
        {"supplier": supplier}
    )






@login_required
def returns_list(request):
    returns = Return.objects.select_related(
        "sale_item__sale",
        "sale_item__product"
    ).order_by("-date")

    return render(
        request,
        "core/returns.html",
        {"returns": returns}
    )





@login_required
def mobile_admin(request):
    return render(request, "core/mobile_admin.html")