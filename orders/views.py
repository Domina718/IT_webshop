from django.shortcuts import render, redirect, get_object_or_404
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart, DatabaseCart
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from shop.models import Product

def order_create(request):

    if request.user.is_authenticated:
        cart = DatabaseCart(request.user)
    else:
        cart = Cart(request)

    if len(cart) == 0:
        return redirect('shop:product_list')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():

            for item in cart:

                if item['quantity'] > item['product'].stock:
                    messages.error(
                        request,
                        f"Not enough stock for {item['product'].name}."
                    )
                    return redirect ('cart:cart_detail')
                
            try:

                with transaction.atomic():

                    order = form.save(commit=False)

                    if request.user.is_authenticated:
                        order.user = request.user

                    order.save()

                    for item in cart:

                        product = Product.objects.select_for_update().get(
                            pk = item['product'].pk
                        )

                        if product.stock < item['quantity']:

                            raise ValidationError(f"Not enough stock for {product.name}.")

                        OrderItem.objects.create(
                            order = order,
                            product = product,
                            price = Decimal(item['price']),
                            quantity = item['quantity']
                        )
                    
                        product.stock -= item['quantity']
                        product.save()

            except ValidationError as e:

                messages.error(request, str(e))

                return redirect ('orders:order_create')

            cart.clear()

            return render(
                request,
                'orders/order_success.html',
                {'order': order}
            )
        
    else:
       
        initial_data = {}

        if request.user.is_authenticated:
           
            profile = request.user.profile

            initial_data = {
               'first_name': profile.first_name,
               'last_name': profile.last_name,
               'email': request.user.email,
               'phone': profile.phone,
               'country': profile.country,
               'address': profile.address,
               'city': profile.city,
               'postal_code': profile.postal_code,
            }

        form = OrderCreateForm(
            initial = initial_data
        )

    return render(
        request, 
        'orders/checkout.html',
        {
            'cart' : cart,
            'form' : form,
            'total' : cart.get_total_price()
        }
    )

@login_required
def my_orders(request):
    orders = Order.objects.filter(user = request.user)
    return render(request, 'orders/my_orders.html', {'orders': orders})

def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id = order_id,
        user = request.user
    )

    return render(request, 'orders/order_detail.html', {'order': order})

def guest_order_detail(request, token):

    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        token = token
    )

    return render(request,'orders/order_detail.html',{'order': order})