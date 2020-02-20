from django import forms

class KeywordsForm(forms.Form):
    keywords = forms.FileField(widget=forms.FileInput(attrs={'accept': ".txt"}))
    model = forms.FileField(widget=forms.FileInput(attrs={'accept': ".model"}))
    quantity = forms.IntegerField(min_value=1)
    language = forms.CharField()
    startdate = forms.DateField()
    enddate = forms.DateField()
