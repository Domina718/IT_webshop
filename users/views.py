from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from orders.models import Order
from .forms import RegisterForm



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(request, "Account created successfully!")
            return redirect('shop:product_list')
        
        else: 
            messages.error(request, "Please fix the errors below.")
        
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user)

    return render(request, 'users/profile.html', {'orders': orders})