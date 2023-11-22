from django import forms


class ReportForm(forms.Form):
  start_date = forms.DateField(
      label="Від",
      widget=forms.DateInput(attrs={
          'id': 'start_date',
          'name': 'start_date',
          'type': 'date',
          'required': True,
      })
  )
  end_date = forms.DateField(
      label="До",
      widget=forms.DateInput(attrs={
          'id': 'end_date',
          'name': 'end_date',
          'type': 'date',
          'required': True,
      })
  )
