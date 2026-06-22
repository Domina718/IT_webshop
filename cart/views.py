from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Product
from .cart import Cart, DatabaseCart
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import UserCart, UserCartItem

@require_POST
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product, 
        id = product_id
    )

    quantity = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        
        user_cart, created = UserCart.objects.get_or_create(
            user = request.user
        )

        existing_item = UserCartItem.objects.filter(
            cart = user_cart,
            product = product
        ).first()

        if existing_item:
            new_quantity = existing_item.quantity + quantity
        else:
            new_quantity = quantity

        if existing_item:
            new_quantity = existing_item.quantity + quantity
        else:
           new_quantity = quantity

        if new_quantity > product.stock:

                messages.error(
                    request, 
                    f"Only {product.stock} units of {product.name} are available."
                )

                return redirect(
                    request.META.get(
                        'HTTP_REFERER',
                        'shop:product_list'
                    )
                )
        
        cart_item, created = UserCartItem.objects.get_or_create(
            cart = user_cart,
            product = product
        )
        
        cart_item.quantity = new_quantity
        cart_item.save()

    else:
        cart = Cart(request)

        current_quantity = 0

        if str(product.id) in cart.cart:
            current_quantity = cart.cart[str(product.id)]['quantity']

        new_quantity = current_quantity + quantity

        if new_quantity > product.stock:
            messages.error(
                request,
                f"Only {product.stock} units of {product.name} are available."
            )

            return redirect(
                request.META.get(
                    'HTTP_REFERER',
                    'shop:product_list'
                )
            )

        cart.add(product_id, quantity)

    messages.success(
        request,
        f"{product.name} added to cart ✓"
    )

    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))
    


def remove_from_cart(request, product_id):

    if request.user.is_authenticated:
        
        user_cart, created = UserCart.objects.get_or_create(
            user = request.user
        )

        item = get_object_or_404(
            UserCartItem,
            cart = user_cart,
            product_id = product_id
        )

        item.delete()

    else:

        cart = Cart(request)
        cart.remove(product_id)

    return redirect('cart:cart_detail')

@require_POST
def update_cart(request, product_id):

    quantity = int(request.POST.get('quantity'))

    if request.user.is_authenticated:

        user_cart, created = UserCart.objects.get_or_create(
            user = request.user
        )

        item = get_object_or_404(
            UserCartItem,
            cart = user_cart,
            product_id = product_id
        )

        product = get_object_or_404(
            Product,
            id = product_id
        )

        if quantity > product.stock:

            item.quantity = product.stock
            item.save()

            messages.error(
                request,
                f"Only {product.stock} units of {product.name} are available. Quantity was adjusted."
            )

            return redirect ('cart:cart_detail')

        if quantity <= 0:
            item.delete()
        else: 
            item.quantity = quantity
            item.save()
    else:
        
        product = get_object_or_404(
            Product,
            id = product_id
        )

        if quantity > product.stock:

            messages.error(
                request,
                f"Only {product.stock} items available."
            )

            return redirect('cart:cart_details')

        cart = Cart(request)
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

    if request.user.is_authenticated:

        cart = DatabaseCart(request.user)

    else:

        cart = Cart(request)

    warnings = check_compatibility(list(cart))

    has_stock_problem = any(
        item['quantity'] > item['product'].stock
        for item in cart
    )

    return render(request, 'cart/cart_detail.html', {
            'cart': cart,
            'total_price': cart.get_total_price(),
            'compatibility_warnings': warnings,
            'has_stock_problem': has_stock_problem

    })