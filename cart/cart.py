from shop.models import Product
from .models import UserCart

class Cart:
    def __init__(self, request):

        self.session = request.session

        cart = self.session.get('cart', {})

        self.cart = cart


    def add(self, product_id, quantity = 1, override_quantity=False):
        product_id = str(product_id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(self.get_price(product_id))
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity

        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    
    def remove(self, product_id):
        product_id = str(product_id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()


    def update(self, product_id, quantity):
        product_id = str(product_id)

        if product_id not in self.cart:
            return

        if quantity <=0:
            self.remove(product_id)
        else:
            self.cart[product_id]['quantity'] = quantity
            self.save()


    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True


    def get_price(self, product_id):
        product = Product.objects.get(id = product_id)
        return product.discount_price
    

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart = {
            product_id: item.copy()
            for product_id, item in self.cart.items()
        }

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = float(item['product'].discount_price)
            item['original_price'] = float(item['product'].price)
            item['has_discount'] = item['product'].has_discount
            item['discount_percent'] = item['product'].discount_percent
            item['total_price'] = item['price'] * item['quantity']
            yield item


    def get_total_price(self):
        return sum(
            item['product'].discount_price * item['quantity']
            for item in self
        )
    

    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True


    def __len__(self):
        return sum(
            item['quantity']
            for item in self.cart.values()
        )
    
    

class DatabaseCart:

    def __init__(self, user):
        self.user_cart, created = UserCart.objects.get_or_create(
            user = user
        )

    def __iter__(self):

        for item in self.user_cart.items.select_related('product'):

            yield {
                'product': item.product,
                'quantity': item.quantity,
                'price': float(item.product.discount_price),
                'original_price': float(item.product.price),
                'has_discount': item.product.has_discount,
                'discount_percent': item.product.discount_percent,
                'total_price': float(item.product.price * item.quantity)
            }
        
    def __len__(self):

        return sum(
            item.quantity
            for item in self.user_cart.items.all()
        )

    def get_total_price(self):

        return sum(
            item.product.discount_price * item.quantity
            for item in self.user_cart.items.select_related('product')
        )
    
    def clear(self):
        self.user_cart.items.all().delete()