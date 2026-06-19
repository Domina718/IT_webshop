from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from orders.models import Order
from .forms import RegisterForm, ProfileForm, CustomPasswordChangeForm
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


@login_required
def change_password(request):

    if request.method == 'POST':

        form = CustomPasswordChangeForm(
            user = request.user,
            data = request.POST
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Password changed successfully!"
            )

            return redirect('users:profile')
    else:

        form = CustomPasswordChangeForm(
            user = request.user
        )

    return render(
        request,
        'users/change_password.html',
        {
            'form': form
        }
    )


def custom_logout(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect('shop:product_list')

class CustomLoginView(LoginView):

    template_name = 'registration/login.html'

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:

            return redirect('users:profile')
        
        return super().dispatch(
            request,
            *args,
            **kwargs
        )