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

        user_cart.save()

        cart = DatabaseCart(request.user)

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

    compatibility_warnings = check_compatibility(list(cart))
    
    product_related_warnings = [
        warning for warning in compatibility_warnings
        if product.name in warning
    ]

    if quantity_to_add < requested_quantity:
            return JsonResponse({
                    "ok": True,
                    "type": "warning",
                    "message": f"Only {quantity_to_add}x {product.name} added. Stock limit reached.",
                    "compatibility_warnings": compatibility_warnings,
                    "product_related_warnings": product_related_warnings,
                })

    
    return JsonResponse({
                    "ok": True,
                    "type": "success",
                    "message": f"{quantity_to_add}x {product.name} added to cart ✓",
                    "compatibility_warnings": compatibility_warnings,
                    "product_related_warnings": product_related_warnings,
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
            user_cart.save()
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
                    "compatibility_warnings": check_compatibility(list(cart))
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

        user_cart.save()

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

    products = []

    for item in cart_items:
        products.append(item['product'])

    cpus = [
        product for product in products 
        if product.socket and product.category.name.lower() == "cpu"
    ]

    motherboards_with_socket = [
        product for product in products 
        if product.socket and product.category.name.lower() in ["motherboard", "motherboards"]
    ]
    
    for cpu in cpus:
        for motherboard in motherboards_with_socket:
            if cpu.socket != motherboard.socket:
                warnings.append(
                    f"<strong>{cpu.name}</strong> ({cpu.socket}) is not compatible with "
                    f"<strong>{motherboard.name}</strong> ({motherboard.socket})." 
                )
    ram_modules = [
        product for product in products 
        if product.ram_type and product.category.name.lower() == "ram"   
    ]
    
    motherboards_with_ram = [
        product for product in products 
        if product.ram_type and product.category.name.lower() in ["motherboard", "motherboards"]
    ]

    for ram in ram_modules:
        for motherboard in motherboards_with_ram:
            if ram.ram_type != motherboard.ram_type:
                warnings.append(
                    f"<strong>{ram.name}</strong> ({ram.ram_type}) is not compatible with "
                    f"<strong>{motherboard.name}</strong> ({motherboard.ram_type})." 
                )

    nvme_ssds = [
        product for product in products 
        if product.storage_type and product.storage_type.lower() == "nvme" and product.category.name.lower() == "ssd"
    ]

    motherboards_for_nvme = [
        product for product in products 
        if product.category.name.lower() in ["motherboard", "motherboards"]
    ]

    for ssd in nvme_ssds:
        for motherboard in motherboards_for_nvme:
            if not motherboard.nvme_support:
                warnings.append(
                    f"<strong>{ssd.name}</strong> requires NVMe support, "
                    f"but <strong>{motherboard.name}</strong> does not support NVMe SSDs." 
                )

    gpus = [
        product for product in products 
        if product.category.name.lower() == "gpu"   
    ]
    
    psus = [
        product for product in products 
        if product.psu_wattage
    ]

    for gpu in gpus:
        if gpu.power_required:
            for psu in psus:
                if psu.psu_wattage < gpu.power_required:
                    warnings.append(
                        f"<strong>{gpu.name}</strong> requires at least {gpu.power_required}W, "
                        f"but <strong>{psu.name}</strong> provides ({psu.psu_wattage})W." 
                    )
    
    cases = [
        product for product in products
        if product.max_gpu_length
    ]

    for gpu in gpus:
        if gpu.gpu_length:
            for case in cases:
                if gpu.gpu_length > case.max_gpu_length:
                    warnings.append(
                        f"<strong>{gpu.name}</strong> ({gpu.gpu_length} mm) does not fit in "
                        f"<strong>{case.name}</strong> (max {case.max_gpu_length} mm)." 
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


