from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import (
    Product, Category,
    Cart, Order, OrderItem,
    UserProfile
)
# ---------------- HOME ----------------
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    query = request.GET.get('q')
    category_id = request.GET.get('category')

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    cart_product_ids = []
    if request.user.is_authenticated:
        cart_product_ids = Cart.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    context = {
        'products': products,
        'categories': categories,
        'cart_product_ids': list(cart_product_ids),
    }
    return render(request, 'home.html', context)



# ---------------- AUTH ----------------
from .forms import RegisterForm
from .models import UserProfile

def register(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        mobile = request.POST['mobile']
        pincode = request.POST['pincode']
        address = request.POST['address']

        username = email  # simple & unique

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        UserProfile.objects.create(
            user=user,
            full_name=f"{first_name} {last_name}",
            email=email,
            mobile=mobile,
            pincode=pincode,
            address=address
        )

        return redirect('login')

    return render(request, 'auth/register.html')


def user_login(request):
    form = AuthenticationForm()

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')

    return render(request, 'auth/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('/') 


# ---------------- CART ----------------
@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1

    cart_item.save()
    return redirect('view_cart')


@login_required
def view_cart(request):
    items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in items)

    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })


@login_required
def remove_cart(request, item_id):
    Cart.objects.get(id=item_id).delete()
    return redirect('view_cart')


# ---------------- ORDER / CHECKOUT ----------------
from .models import Order, OrderItem

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items:
        return redirect('view_cart')

    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            status="Payment Successful"
        )

        # 🔥 SAVE ORDER ITEMS (CRITICAL)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()
        return redirect('orders')

    return render(request, 'checkout.html', {'total': total})

from django.contrib.auth.decorators import login_required

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'product_detail.html', {'product': product})

from django.contrib.auth.decorators import login_required
from .models import UserProfile

@login_required
def my_account(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'account.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        profile.full_name = request.POST.get('full_name')
        profile.email = request.POST.get('email')
        profile.mobile = request.POST.get('mobile')
        profile.address = request.POST.get('address')
        profile.save()
        return redirect('my_account')

    return render(request, 'edit_profile.html', {'profile': profile})

@login_required
def update_cart_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if request.method == "POST":
        qty = int(request.POST.get('quantity', 1))

        if qty > 0 and qty <= cart_item.product.stock:
            cart_item.quantity = qty
            cart_item.save()

    return redirect('view_cart')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})
from django.http import HttpResponseRedirect

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1

    cart_item.save()

    # 🔥 Redirect back to same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))