from django import forms
from cases.models import Sample


class CompareSamplesForm(forms.Form):
    sample_a = forms.ModelChoiceField(
        queryset=Sample.objects.all(),
        label="Sample A"
    )
    sample_b = forms.ModelChoiceField(
        queryset=Sample.objects.all(),
        label="Sample B"
    )

    def clean(self):
        cleaned_data = super().clean()
        a = cleaned_data.get("sample_a")
        b = cleaned_data.get("sample_b")
        if a and b and a.id == b.id:
            raise forms.ValidationError("Sample A and Sample B must be different.")
        return cleaned_data


class SearchMatchesForm(forms.Form):
    query_sample = forms.ModelChoiceField(
        queryset=Sample.objects.all(),
        label="Query Sample"
    )
