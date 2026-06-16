from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Q, Count
from .models import Product, Category, Review
from .forms import ReviewForm


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
        Product.objects.annotate(avg_rating=Avg('reviews__rating')), 
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

    user_review = None

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
    })