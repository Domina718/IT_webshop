from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile
from .validators import phone_validator, postal_code_validator, text_validator


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

    phone = forms.CharField(
        required=False,
        validators = [phone_validator],
        widget = forms.TextInput(attrs={
            'placeholder': '+385 91 234 5678'
        })
    )

    city = forms.CharField(
        validators = [text_validator],
        widget = forms.TextInput(attrs={
            'placeholder':'Split'
        })
    )

    country = forms.CharField(
        required=False,
        validators = [text_validator],
        widget = forms.TextInput(attrs={
            'placeholder': 'Croatia'
        })
    )

    postal_code = forms.CharField(
        validators = [postal_code_validator],
        widget = forms.TextInput(attrs={
            'placeholder': '21000'
        })
    )

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

        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'John'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Smith'
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Main Street 10'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            
            field.widget.attrs.update({
                'class': 'form-control'
            })

class CustomPasswordResetForm(SetPasswordForm):

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')

        if self.user.check_password(password):
            raise forms.ValidationError(
                "New password cannot be the same as your current password."
            )
        return password
    
class CustomPasswordChangeForm(PasswordChangeForm):

    def clean_new_password1(self):

        password = self.cleaned_data.get('new_password1')

        if self.user.check_password(password):

            raise forms.ValidationError(
                "New password cannot be the same as your current password."
            )
        return password