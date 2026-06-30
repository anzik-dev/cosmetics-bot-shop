from django import forms
from .models import Review
from .models import ProductImage

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Оставьте ваш отзыв'}),
            'rating': forms.RadioSelect(choices=[(i, '') for i in range(5, 0, -1)]),
        }
        labels = {
            'text': 'Отзыв:',
            'rating': 'Оценка (1-5 звёзд):',
        }
    
