from .cart import Cart, DatabaseCart

def cart(request):

    if request.user.is_authenticated:

        return {'cart': DatabaseCart(request.user)}
    
    else:

        return {'cart': Cart(request)}