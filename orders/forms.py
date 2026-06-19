from django import forms
from .models import Order
from users.validators import phone_validator, postal_code_validator, text_validator

class OrderCreateForm(forms.ModelForm):

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
        model = Order

        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'country',
            'address',
            'city',
            'postal_code'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'John'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Smith'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'john@example.com'
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

        