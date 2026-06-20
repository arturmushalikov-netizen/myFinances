from django import forms
from .models import MonthlyFin


class MonthlyFinForm(forms.ModelForm):
    class Meta:
        model = MonthlyFin
        fields = ["start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.month_text = f"{instance.start_date} - {instance.end_date}"
        if commit:
            instance.save()
        return instance
