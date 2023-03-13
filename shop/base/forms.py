from django import forms

class ReportForm(forms.Form):
  start_date = forms.DateField()
  end_date = forms.DateField()