from django import forms

class ProjectNameForm(forms.Form):
  name = forms.CharField(max_length=100)

class ProjectPriceForm(forms.Form):
  price = forms.DecimalField()
