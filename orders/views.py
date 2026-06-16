from django.shortcuts import render, redirect, get_object_or_404
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from django.contrib.auth.decorators import login_required
from decimal import Decimal

#@login_required
def order_create(request):

    cart = Cart(request)

    if len(cart) == 0:
        return redirect('shop:product_list')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():

            order = form.save(commit=False)

            if request.user.is_authenticated:
                order.user = request.user

            order.save()

            for item in cart:

                OrderItem.objects.create(
                    order = order,
                    product = item['product'],
                    price = Decimal(item['price']),
                    quantity = item['quantity']
                )

            cart.clear()

            return render(
                request,
                'orders/order_success.html',
                {'order': order}
            )
        
    else:
        form = OrderCreateForm()

    return render(
        request, 
        'orders/checkout.html',
        {
            'cart' : cart,
            'form' : form
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

