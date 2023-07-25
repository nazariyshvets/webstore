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


class CommentForm(forms.Form):
    comment_text = forms.CharField(widget=forms.Textarea)


class EvaluationForm(forms.Form):
    evaluation = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': 1,
            'max': 5,
            'step': 1,
            'list': 'tickmarks',
        })
    )

    def clean_evaluation(self):
        """
        Custom validation for the evaluation field to ensure it's an integer between 1 and 5.
        """
        evaluation = self.cleaned_data['evaluation']
        if not 1 <= evaluation <= 5:
            raise forms.ValidationError(
                "Оцінка повинна бути в межах від 1 до 5")
        return evaluation