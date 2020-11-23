from django import forms
from .models import Classroom,User

class Classroom_form(forms.ModelForm):
    owner = forms.ModelChoiceField(User.objects.all(),widget=forms.HiddenInput())
    class Meta:
        model=Classroom
        fields=['owner',
        'title',
        'description',
        'start_time',
        'end_time',
        'fee',
        'sunday',
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday']

class ImageForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()        