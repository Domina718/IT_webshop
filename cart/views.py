from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Product
from .cart import Cart
from django.views.decorators.http import require_POST
from django.contrib import messages

@require_POST
def add_to_cart(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(
        Product, 
        id = product_id
    )

    quantity = int(request.POST.get('quantity', 1))

    cart.add(product_id, quantity)

    messages.success(
        request,
        f"{product.name} added to cart ✓"
    )

    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))


def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)

    return redirect('cart:cart_detail')

@require_POST
def update_cart(request, product_id):
    cart = Cart(request)

    quantity = int(request.POST.get('quantity'))

    cart.update(product_id, quantity)

    return redirect('cart:cart_detail')

def check_compatibility(cart_items):
    warnings = []

    sockets = {}
    ram_types = {}

    products = []

    for item in cart_items:

        product = item['product']
        products.append(product)

        if product.socket:
            sockets.setdefault(
                product.socket,
                []
            ).append(product.name)

        if product.ram_type:
            ram_types.setdefault(
                product.ram_type,
                []
            ).append(product.name)

    if len(sockets) > 1:
        warnings.append(
            "Socket mismatch: " + ", ".join(
                [
                    f"{socket}: {', '.join(products)}"
                    for socket, products in sockets.items()
                ]
            )
        )

    if len(ram_types) > 1:
        warnings.append(
            "RAM type mismatch: " + ", ".join(
                [
                    f"{ram}: {', '.join(products)}"
                    for ram, products in ram_types.items()
                ]
            )
        )

    for gpu in products:
        
        if gpu.power_required:

            for psu in products:

                if psu.psu_wattage:

                    if psu.psu_wattage < gpu.power_required:

                        warnings.append(
                            f"{gpu.name} requires "
                            f"{gpu.power_required}W PSU, "
                            f"but {psu.name} has "
                            f"{psu.psu_wattage}W."
                        )

    for gpu in products:
        
        if gpu.gpu_length:

            for case in products:

                if case.max_gpu_length:

                    if gpu.gpu_length > case.max_gpu_length:

                        warnings.append(
                            f"{gpu.name} does not fit in "
                            f"{case.name}. "
                            f"GPU length: {gpu.gpu_length}mm, "
                            f"case supports: {case.max_gpu_length}mm."
                        )

    return warnings


def cart_detail(request):
    cart = Cart(request)

    warnings = check_compatibility(list(cart))

    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'total_price': cart.get_total_price(),
        'compatibility_warnings': warnings

    })