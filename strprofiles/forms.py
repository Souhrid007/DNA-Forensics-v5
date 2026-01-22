from django import forms

class STRUploadForm(forms.Form):
    file = forms.FileField(
        label="STR Profile CSV",
        help_text="Upload CSV with columns: locus, allele1, allele2"
    )
