from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Product
from .cart import Cart
from django.views.decorators.http import require_POST

@require_POST
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id = product_id)

    quantity = int(request.POST.get('quantity', 1))
    cart.add(product_id, quantity)

    return redirect('cart:cart_detail')


def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)

    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)

    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'total': cart.get_total_price()
    })

@require_POST
def update_cart(request, product_id):
    cart = Cart(request)

    quantity = int(request.POST.get('quantity'))

    cart.update(product_id, quantity)

    return redirect('cart:cart_detail')

def check_compatibility(cart_items):
    warnings = []

    sockets = set()
    ram_types = set()

    for item in cart_items:
        product = item['product']

        if product.socket:
            sockets.add(product.socket)

        if product.ram_type:
            ram_types.add(product.ram_type)

    if len(sockets) > 1:
        warnings.append("Socket mismatch detected in cart!")

    if len(ram_types) > 1:
        warnings.append("RAM type mismatch detected in cart!")

    return warnings


def cart_detail(request):
    cart = Cart(request)

    warnings = check_compatibility(list(cart))

    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'total_price': cart.get_total_price(),
        'compatibility_warnings': warnings

    })