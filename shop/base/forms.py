from django import forms


class CommentForm(forms.Form):
  comment = forms.CharField(widget=forms.Textarea)


class EvaluationForm(forms.Form):
  evaluation = forms.IntegerField(
      widget=forms.NumberInput(attrs={
          "type": "range",
          "min": 1,
          "max": 5,
          "step": 1,
          "list": "tickmarks",
      })
  )

  def clean_evaluation(self):
    """
    Custom validation for the evaluation field to ensure it"s an integer between 1 and 5.
    """
    evaluation = self.cleaned_data["evaluation"]
    if not 1 <= evaluation <= 5:
      raise forms.ValidationError(
          "Оцінка повинна бути в межах від 1 до 5")
    return evaluation
