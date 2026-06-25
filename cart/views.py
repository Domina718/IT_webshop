from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Product
from .cart import Cart, DatabaseCart
from django.views.decorators.http import require_POST
from .models import UserCart, UserCartItem
from django.http import JsonResponse


@require_POST
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product, 
        id = product_id
    )

    requested_quantity = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        
        user_cart, created = UserCart.objects.get_or_create(
            user = request.user
        )

        existing_item = UserCartItem.objects.filter(
            cart = user_cart,
            product = product
        ).first()

        current_quantity = existing_item.quantity if existing_item else 0
        available_quantity = product.stock - current_quantity

        if available_quantity <= 0:
            return JsonResponse({  
                    "ok": False,
                    "type": "warning",
                    "message": f"No more units of {product.name} are available."
                })
        
        quantity_to_add = min(requested_quantity, available_quantity)
        new_quantity = current_quantity + quantity_to_add

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

        available_quantity = product.stock - current_quantity

        if available_quantity <= 0:

            return JsonResponse({  
                    "ok": False,
                    "type": "warning",
                    "message": f"No more units of {product.name} are available."
            })
        
        quantity_to_add = min(requested_quantity, available_quantity)
        cart.add(product_id, quantity_to_add)

    if quantity_to_add < requested_quantity:


            return JsonResponse({
                    "ok": True,
                    "type": "warning",
                    "message": f"Only {quantity_to_add}x {product.name} added. Stock limit reached."
                })
    
    return JsonResponse({
                    "ok": True,
                    "type": "success",
                    "message": f"{quantity_to_add}x  {product.name} added to cart ✓"
                })



def remove_from_cart(request, product_id):

    product = Product.objects.filter(id=product_id).first()
    product_name = product.name if product else "Item"

    if request.user.is_authenticated:

        cart = DatabaseCart(request.user)
        
        user_cart, _ = UserCart.objects.get_or_create(
            user = request.user
        )

        item = UserCartItem.objects.filter(
            cart = user_cart,
            product_id = product_id
        ).first()

        if item:
            removed_qty = item.quantity
            item.delete()
        else:
            removed_qty = 0

    else:
        cart = Cart(request)

        removed_qty = cart.cart.get(str(product_id), {}).get("quantity", 0)
        cart.remove(product_id)

    return JsonResponse({
                    "ok": True,
                    "type": "success",
                    "message": f"{removed_qty}x {product_name} removed from cart",
                    "product_id": product_id,
                    "removed_qty": removed_qty,
                    "cart_count": len(cart),
                    "cart_total": cart.get_total_price(),
                    "original_cart_total": float(cart.get_original_total_price()),
                    "total_savings": float(cart.get_total_savings()),
                })


@require_POST
def update_cart(request, product_id):

    quantity = int(request.POST.get('quantity'))

    product = get_object_or_404(Product,id = product_id)

    warning = None
    deleted = False
           
    if request.user.is_authenticated:

        cart = DatabaseCart(request.user)

        user_cart, _ = UserCart.objects.get_or_create(
            user = request.user
        )

        item = get_object_or_404(
            UserCartItem,
            cart = user_cart,
            product_id = product_id
        )

        if quantity > product.stock:

            quantity = product.stock
            warning = f"Only {product.stock} units of {product.name} are available. Quantity adjusted."

        deleted = False
        
        if quantity <= 0:
            item.delete()
            deleted = True
        else: 
            item.quantity = quantity
            item.save()
    else:
        
        cart = Cart(request)

        if quantity > product.stock:
            quantity = product.stock
            warning = f"Only {product.stock} units of {product.name} are available. Quantity adjusted."
           
        if quantity <= 0:
            cart.remove(product_id)
            deleted = True
        else:
            cart.update(product_id, quantity)

    return JsonResponse({
                    "ok": True,
                    "deleted": deleted,
                    "type": "warning" if warning else "success",
                    "message": warning if warning else "",
                    "product_name": product.name,
                    "adjusted_quantity": quantity,
                    "item_total": float(product.discount_price * quantity),
                    "cart_total": float(cart.get_total_price()),
                    "cart_count": len(cart),
                    "original_item_total":float(product.price * quantity),
                    "has_discount": product.has_discount,
                    "discount_percent": product.discount_percent,
                    "original_cart_total": float(cart.get_original_total_price()),
                    "total_savings": float(cart.get_total_savings()),
                })

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
            'has_stock_problem': has_stock_problem,
            'original_total_price': cart.get_original_total_price(),
            'total_savings': cart.get_total_savings()

    })

def cart_count(request):
    if request.user.is_authenticated:
        cart = DatabaseCart(request.user)
    else:
        cart = Cart(request)
    return JsonResponse({
        "count": len(cart)
    })

def mini_cart(request):
    if request.user.is_authenticated:
        cart = DatabaseCart(request.user)
    else:
        cart = Cart(request)

    items = []

    for item in cart:
        items.append({
            "name": item["product"].name,
            "quantity": item["quantity"],
            "price": float(item["price"]),
            "original_price": float(item["original_price"]),
            "total_price": float(item["total_price"]),
            "has_discount": item["has_discount"],
            "discount_percent": item["discount_percent"],
            "image": item["product"].image.url if item["product"].image else "",
        })

    return JsonResponse({
        "count": len(cart),
        "total": float(cart.get_total_price()),
        "items": items[:5]
    })


