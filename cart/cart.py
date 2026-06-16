from shop.models import Product



class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = {}
            self.session['cart'] = cart
        self.cart = cart

        if 'cart' not in self.session:
            self.session['cart'] = {}

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
        return product.price

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = float(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
        #for product in products:
            #yield{
            #    'product': product,
            #    'quantity': self.cart[str(product.id)],
            #    'total': product.price * self.cart[str(product.id)]
            #}

    def get_total_price(self):
        return sum(
            item['product'].price * item['quantity']
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
    
    #def decrease(self, product_id):
    #    product_id = str(product_id)

    #    if product_id in self.cart:
    #        self.cart[product_id] -= 1

    #        if self.cart[product_id] <= 0:
    #            del self.cart[product_id]

    #        self.save()


