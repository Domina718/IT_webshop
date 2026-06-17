from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ProfileForm(forms.ModelForm):

    class Meta: 
        model = Profile


        fields = [
            'first_name',
            'last_name',
            'phone',
            'country',
            'address',
            'city',
            'postal_code',
        ]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            for field in self.fields.values():
                field.widget.attrs.update({
                    'class': 'form-control'
                })