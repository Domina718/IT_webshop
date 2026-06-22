from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Q, Count
from .models import Product, Category, Review
from compatibility.models import CompatibilityRule
from .forms import ReviewForm
from .models import Product


def product_list(request):

    products = Product.objects.all()
        
    categories = Category.objects.all()

    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min', '')
    max_price = request.GET.get('max', '')

    if query:
        products = products.filter(
            Q(name__icontains = query) |
            Q(description__icontains = query)
        )

    if category_id:
        products = products.filter(category_id = category_id)

    if min_price and min_price.strip() != "":
        products = products.filter(price__gte=float(min_price))

    if max_price and max_price.strip() != "":
        products = products.filter(price__lte=float(max_price))

    products = products.annotate(
        avg_rating = Avg('reviews__rating'),
        review_count = Count('reviews')
    )

    for product in products:
        if product.avg_rating:
            product.rating_percent = float(product.avg_rating / 5 * 100)

    return render(request, 'shop/product_list.html',{
        'products': products,
        'categories' : categories,
        'query' : query,
        'category_id': category_id,
        'min_price': min_price,
        'max_price': max_price
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

    if request.user.is_authenticated:
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
    })

def home(request):

    products = Product.objects.all()[:8]

    return render(request, 'shop/home.html', {'products': products})