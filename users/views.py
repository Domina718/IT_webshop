from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from orders.models import Order
from .forms import RegisterForm, ProfileForm
from .models import Profile



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

    profile, created = Profile.objects.get_or_create(
        user = request.user
    )

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            instance = profile
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Profile updated sucessfully!"
            )

            return redirect('users:profile')
        
    else:
        form = ProfileForm(
            instance = profile
        )

    orders = Order.objects.filter(
        user = request.user
    )

    return render(
        request, 
        'users/profile.html',
        {
            'form': form,
            'orders': orders
        }
    )
    
@login_required
def edit_profile(request):

    profile, created = Profile.objects.get_or_create(
        user = request.user
    )


    if request.method == 'POST':

        form = ProfileForm(
            request.POST,
            instance = profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully!"
            )

            return redirect('users:profile')
        
    else:

        form = ProfileForm(
            instance = profile
        )

    
    return render(
        request, 
        'users/edit_profile.html',
        {
            'form': form
        }
    )