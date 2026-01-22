from django import forms
from .models import Sample, Case


class SampleFileUploadForm(forms.Form):
    file = forms.FileField(
        label="DNA File (FASTA/FASTQ)",
        help_text="Upload the raw DNA file for this sample."
    )


class SampleCreateForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ['sample_id', 'case', 'fingerprint_id', 'collected_at', 'notes']
        widgets = {
            'collected_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format="%Y-%m-%dT%H:%M"
            )
        }
        help_texts = {
            'sample_id': 'Unique ID for this DNA evidence (e.g., SAM2025-003).',
            'case': 'Select the forensic case this evidence belongs to.',
            'fingerprint_id': 'Optional related fingerprint or person identifier.',
            'collected_at': 'Time when the sample was collected (optional).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow empty collected_at
        self.fields['collected_at'].input_formats = ["%Y-%m-%dT%H:%M"]
