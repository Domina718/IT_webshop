def check_cart_compatibility(cart_items):

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
        warnings.append("Socket mismatch detected between products in cart.")

    if len(ram_types) > 1:
        warnings.append("RAM type mismatch detected between products in cart.")

    return warnings