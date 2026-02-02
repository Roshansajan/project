from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max
from django.core.exceptions import ObjectDoesNotExist
import datetime
from .models import *
from .forms import *

# Create your views here.

def home(request):
    categories = Category.objects.all()[:3]
    
    new_arrivals = Product.objects.filter(is_available=True).order_by('-created_at')[:8]
    
    best_sellers = Product.objects.filter(is_available=True).order_by('?')[:8]
    
    related_products = Product.objects.filter(is_available=True).order_by('?')[:8]

    context = {
        'categories': categories,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'related_products': related_products,
    }
    return render(request, 'index.html', context)


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    context = {'form': form}
    return render(request, 'login.html', context)

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            messages.success(request, "Registration successful! Welcome.")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, 'register.html', context)

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

def shop(request):
    products = Product.objects.filter(is_available=True)

    category_name = request.GET.get('category')    
    query = request.GET.get('q')                   
    sort_by = request.GET.get('sort')              
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    if category_name:
        products = products.filter(category__name=category_name)

    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    if sort_by == 'popularity':
        products = products.order_by('-stock') 
    elif sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    categories = Category.objects.all()
    price_stats = Product.objects.aggregate(Min('price'), Max('price'))
    min_limit = price_stats['price__min'] or 0
    max_limit = price_stats['price__max'] or 200

    paginator = Paginator(products, 10) 
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context = {
        'products': products_page,
        'categories': categories,
        'min_limit': min_limit,
        'max_limit': max_limit,
        'current_category': category_name,
        'current_sort': sort_by,
        'current_min_price': min_price,
        'current_max_price': max_price,
    }
    return render(request, 'shop.html', context)

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    
    related_products = Product.objects.filter(
        category=product.category, 
        is_available=True
    ).exclude(id=id)[:5]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product_details.html', context)
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = get_object_or_404(Product, id=product_id)
    
    selected_color = None
    selected_size = None
    
    if request.method == 'POST':
        color_id = request.POST.get('color')
        if color_id:
            selected_color = Color.objects.get(id=color_id)

        size_id = request.POST.get('size')
        if size_id:
            selected_size = Size.objects.get(id=size_id)
        

        quantity = int(request.POST.get('quantity', 1))
        

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()


        is_cart_item_exists = CartItem.objects.filter(
            product=product, 
            cart=cart, 
            color=selected_color, 
            size=selected_size
        ).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.get(
                product=product, 
                cart=cart, 
                color=selected_color, 
                size=selected_size
            )
            cart_item.quantity += quantity 
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = quantity,
                cart = cart,
                color = selected_color,
                size = selected_size
            )
            cart_item.save()
        
        return redirect('cart')

    return redirect('product_detail', id=product_id)

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    return render(request, 'cart.html', context)

def add_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')

def remove_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass 

    tax = (2 * total) / 100 
    grand_total = total + tax

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'checkout.html', context)

def place_order(request):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            cart_count = cart_items.count()
        except Cart.DoesNotExist:
            return redirect('shop')

        if cart_count <= 0:
            return redirect('shop')

        grand_total = 0
        tax = 0
        total = 0
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
        
        tax = (2 * total) / 100
        grand_total = total + tax

        form = OrderForm(request.POST)
        
        if form.is_valid():
            data = Order()
            if request.user.is_authenticated:
                data.user = request.user 
            else:
                data.user = None
                
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.is_ordered = True
            data.save()

            for item in cart_items:
                order_product = OrderProduct()
                order_product.order_id = data.id
                order_product.product_id = item.product_id
                order_product.quantity = item.quantity
                order_product.product_price = item.product.price
                order_product.color = item.color
                order_product.size = item.size
                order_product.ordered = True
                order_product.save()

                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()

            CartItem.objects.filter(cart=cart).delete()

            messages.success(request, "Your order has been placed successfully!")
            return redirect('home') 
        else:

            print("Form Errors:", form.errors) 
            messages.error(request, "There was an error with your form. Please check the details.")
            return redirect('checkout')
            
    return redirect('checkout')

def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'my_orders.html', context)

def test(request):
    return render(request,'product_details.html')