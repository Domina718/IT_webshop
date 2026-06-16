from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):

    RATING_CHOICES = [(5,5), (4,4), (3,3), (2,2), (1,1)
    ]

    rating = forms.TypedChoiceField(
        choices = RATING_CHOICES,
        coerce = int,
        widget = forms.HiddenInput()
    )
    class Meta:
        model = Review
        fields = ['rating', 'comment']