from django import forms

class KeywordsForm(forms.Form):
    keywords = forms.FileField(widget=forms.FileInput(attrs={'accept': ".txt"}))
    model = forms.FileField(widget=forms.FileInput(attrs={'accept': ".model"}))

