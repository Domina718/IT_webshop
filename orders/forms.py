from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):

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
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            field.widget.attrs.update({
                'class': 'form-control'
            })

        