from django import forms
from .models import MaintenanceRecord


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['asset', 'maintenance_type', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
        # Remap 'problem_description' to 'description'
        if 'problem_description' in self.data:
            self.data['description'] = self.data.get('problem_description')
        # ✅ Remap 'asset_id' to 'asset'
        if 'asset_id' in self.data:
            self.data['asset'] = self.data.get('asset_id')
