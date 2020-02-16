from django import forms

class KeywordsForm(forms.Form):
    keywords = forms.CharField()
