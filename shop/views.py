from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Q, Count
from .models import Product, Category, Review
from compatibility.models import CompatibilityRule
from .forms import ReviewForm
from orders.models import OrderItem


def product_list(request):

    products = Product.objects.all()
        
    categories = Category.objects.all()

    query = request.GET.get('q', '')
    categories_selected = [
        int(category_id)
        for category_id in request.GET.getlist('category')
        if category_id.strip()
    ]
    min_price = request.GET.get('min', '')
    max_price = request.GET.get('max', '')
    brands_selected = [
        item for item in request.GET.getlist('brand')
        if item.strip()
    ]
    sockets_selected = [
        item for item in request.GET.getlist('socket')
        if item.strip()
    ]
    ram_types_selected = [
        item for item in request.GET.getlist('ram_type')
        if item.strip()
    ]
    storage_types_selected = [
        item for item in request.GET.getlist('storage_type')
        if item.strip()
    ]

    stock_status_options = [
        "in_stock",
        "low_stock",
        "out_of_stock",
    ]
    stock_status_selected =  [
        item for item in request.GET.getlist('stock_status')
        if item.strip()
    ]

    if query:
        products = products.filter(
            Q(name__icontains = query) |
            Q(description__icontains = query)
        )

    if categories_selected:
        products = products.filter(category_id__in = categories_selected)

    if min_price and min_price.strip() != "":
        products = products.filter(price__gte=float(min_price))

    if max_price and max_price.strip() != "":
        products = products.filter(price__lte=float(max_price))

    if brands_selected:
        products = products.filter(brand__in = brands_selected)

    if sockets_selected:
        products = products.filter(socket__in = sockets_selected)

    if ram_types_selected:
        products = products.filter(ram_type__in = ram_types_selected)

    if storage_types_selected:
        products = products.filter(storage_type__in = storage_types_selected)
    
    if stock_status_selected:
        stock_query = Q()

        if "in_stock" in stock_status_selected:
            stock_query |= Q(stock__gt=7)
        if "low_stock" in stock_status_selected:
            stock_query |= Q(stock__gt=0, stock__lte=7)
        if "out_of_stock" in stock_status_selected:
            stock_query |= Q(stock=0)

        products = products.filter(stock_query)
        


    brands = Product.objects.exclude(brand='').values_list('brand', flat=True).distinct()
    sockets = Product.objects.exclude(socket='').values_list('socket', flat=True).distinct()
    ram_types = Product.objects.exclude(ram_type='').values_list('ram_type', flat=True).distinct()
    storage_types = Product.objects.exclude(storage_type='').values_list('storage_type', flat=True).distinct()


    products = products.annotate(
        avg_rating = Avg('reviews__rating'),
        review_count = Count('reviews')
    )

    wishlist_product_ids = []

    if request.user.is_authenticated:
        wishlist_product_ids = list(
            request.user.wishlist_items.values_list('product_id', flat=True)
        )

    for product in products:
        if product.avg_rating:
            product.rating_percent = float(product.avg_rating / 5 * 100)

    is_in_wishlist = False

    if request.user.is_authenticated:
        is_in_wishlist = request.user.wishlist_items.filter(
            product = product
        ).exists()

    return render(request, 'shop/product_list.html',{
        'products': products,
        'categories' : categories,
        'query' : query,
        'categories_selected': categories_selected,
        'min_price': min_price,
        'max_price': max_price,
        'brands': brands,
        'sockets': sockets,
        'ram_types': ram_types,
        'storage_types': storage_types,
        'brands_selected': brands_selected,
        'sockets_selected': sockets_selected,
        'ram_types_selected': ram_types_selected,
        'storage_types_selected': storage_types_selected,
        'stock_status_options': stock_status_options,
        'stock_status_selected': stock_status_selected,
        'wishlist_product_ids': wishlist_product_ids,
        'is_in_wishlist': is_in_wishlist,
    })



def product_detail(request, pk):

    product = get_object_or_404(
        Product.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')), 
        pk=pk
    )

    if request.method == 'POST':

        if not request.user.is_authenticated:
            return redirect('login')
        
        can_review = OrderItem.objects.filter(
            order__user = request.user,
            order__status = 'delivered',
            product = product
        ).exists()

        if not can_review:
            return redirect('shop:product_detail', pk = product.pk)

        form = ReviewForm(request.POST)

        if form.is_valid():

            Review.objects.update_or_create(
                product = product,
                user = request.user,
                defaults = {
                    'rating' : form.cleaned_data['rating'],
                    'comment' : form.cleaned_data['comment'],
                }
            )

            return redirect('shop:product_detail', pk = product.pk)



    average_rating = product.avg_rating
    reviews = product.reviews.all()

    compatibility_rules = CompatibilityRule.objects.filter(
        Q(product=product) |
        Q(compatible_product=product)
    ).select_related(
        'product',
        'compatible_product',
        'product__category',
        'compatible_product__category'
    )

    COMPATIBILITY_LABELS = {
        "CPU": "CPUs",
        "Motherboard": "Motherboards",
        "RAM": "RAM Modules",
        "SSD": "SSDs",
        "GPU": "Graphics Cards",
        "PSU": "Power Supplies",
        "Case": "Cases",
    }

    compatibility_groups = {}

    for rule in compatibility_rules:

        if rule.product == product:
            compatible_product = rule.compatible_product
        else:
            compatible_product = rule.product

        label = COMPATIBILITY_LABELS.get(
            compatible_product.category.name, 
            compatible_product.category.name
        )

        compatibility_groups.setdefault(label, [])

        if compatible_product.id not in [
            p.id for p in compatibility_groups[label]
        ]:
            compatibility_groups[label].append(compatible_product)

    if product.category.name == "SSD" and product.storage_type == "NVMe":

        nvme_motherboards = Product.objects.filter(
            category__name = "Motherboard",
            nvme_support = True
        ).exclude(stock=0)

        compatibility_groups.setdefault("Motherboards", [])

        existing_ids = [
            p.id for p in compatibility_groups["Motherboards"]
        ]

        for motherboard in nvme_motherboards:
            if motherboard.id not in existing_ids:
                compatibility_groups["Motherboards"].append(motherboard)

    if product.category.name == "Motherboard" and product.nvme_support:

        nvme_ssds = Product.objects.filter(
            category__name = "SSD",
            storage_type = "NVMe"
        ).exclude(stock=0)

        compatibility_groups.setdefault("SSDs", [])

        existing_ids = [
            p.id for p in compatibility_groups["SSDs"]
        ]

        for ssd in nvme_ssds:
            if ssd.id not in existing_ids:
                compatibility_groups["SSDs"].append(ssd)

    recommended_products = Product.objects.filter(
        order_items__order__items__product = product
    ).exclude(
        id=product.id
    ).annotate(
        purchase_count=Count('id')
    ).order_by(
        '-purchase_count'
    )[:4]

    if average_rating:
        product.rating_percent = float(average_rating / 5 * 100)

    user_review = None
    form = None
    can_review = False

    if request.user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__user = request.user,
            order__status = 'delivered',
            product = product
        ).exists()

        user_review = Review.objects.filter(
            product = product,
            user = request.user
        ).first()

        if user_review:
            form = ReviewForm(instance = user_review)
        else:
            form = ReviewForm()

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'form': form,
        'user_review': user_review,
        'compatibility_groups': compatibility_groups,
        'recommended_products': recommended_products,
        'can_review': can_review,
    })

def home(request):

    discount_products = list(
        Product.objects.filter(discount_percent__gt=0).order_by('-id')
    )

    if len(discount_products) < 4:
        ids = [p.id for p in discount_products]

        extra = Product.objects.exclude(id__in=ids).order_by('-id')[:4-len(discount_products)]

        featured_products = discount_products + list(extra)
    else:
        featured_products = discount_products[:4]

    latest_products = Product.objects.order_by('-id')[:8]



    return render(request, 
                  'shop/home.html', 
                  {
                      'featured_products': featured_products,
                      'latest_products': latest_products,
                  },
    )