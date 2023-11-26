from django import forms


class ReportForm(forms.Form):
  start_date = forms.DateField(
      label="Від",
      widget=forms.DateInput(attrs={
          "id": "start_date",
          "name": "start_date",
          "type": "date",
          "required": True,
      })
  )
  end_date = forms.DateField(
      label="До",
      widget=forms.DateInput(attrs={
          "id": "end_date",
          "name": "end_date",
          "type": "date",
          "required": True,
      })
  )


class ReplenishmentForm(forms.Form):
  amount = forms.DecimalField(
      max_digits=9,
      decimal_places=2,
      label="Сума (грн)",
      widget=forms.NumberInput(attrs={"step": 1}),
  )

  def __init__(self, *args, **kwargs):
    super(ReplenishmentForm, self).__init__(*args, **kwargs)
    self.label_suffix = ""
