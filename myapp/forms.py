from django import forms
from .models import (
    Project, Material, MaterialCategory, MaterialSubcategory,
    MaterialTransaction, Task, Equipment, EquipmentUsage, EquipmentTransfer,
    Warehouse, Subcontractor, CostCenter, CostItem
)

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'project', 'assigned_to',
            'status', 'priority', 'progress', 'start_date', 'due_date'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100})
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')
        
        if start_date and due_date and start_date > due_date:
            raise forms.ValidationError("Start date cannot be later than due date.")
        
        return cleaned_data

class MaterialTransactionForm(forms.ModelForm):
    class Meta:
        model = MaterialTransaction
        fields = [
            'project', 'material', 'transaction_type', 'quantity',
            'unit_price', 'date', 'supplier', 'invoice_number', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'quantity': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'})
        }

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        material = cleaned_data.get('material')
        quantity = cleaned_data.get('quantity')
        
        if transaction_type == 'CONSUMPTION' and material and quantity:
            if quantity > material.current_stock:
                raise forms.ValidationError(
                    f"Cannot consume {quantity} {material.unit}. Only {material.current_stock} {material.unit} available."
                )
        
        return cleaned_data

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'name', 'code', 'category', 'subcategory', 'description',
            'unit', 'unit_price', 'minimum_stock', 'current_stock'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subcategory'].queryset = MaterialSubcategory.objects.select_related('category')

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'code', 'location', 'description', 'start_date',
            'planned_end_date', 'status', 'manager', 'total_budget'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'planned_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'total_budget': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        planned_end_date = cleaned_data.get('planned_end_date')
        
        if start_date and planned_end_date and start_date > planned_end_date:
            raise forms.ValidationError("Start date cannot be later than planned end date.")
        
        return cleaned_data

class MaterialCategoryForm(forms.ModelForm):
    class Meta:
        model = MaterialCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MaterialSubcategoryForm(forms.ModelForm):
    class Meta:
        model = MaterialSubcategory
        fields = ['category', 'name', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ProjectFormNew(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'planned_end_date', 'status', 'progress']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'planned_end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100})
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        planned_end_date = cleaned_data.get('planned_end_date')
        
        if start_date and planned_end_date and start_date > planned_end_date:
            raise forms.ValidationError("Start date cannot be later than planned end date.")
        
        return cleaned_data

class TaskFormNew(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'title', 'description', 'assigned_to', 'start_date', 'due_date', 'status', 'priority']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')
        
        if start_date and due_date and start_date > due_date:
            raise forms.ValidationError("Start date cannot be later than due date.")
        
        return cleaned_data

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'name', 'code', 'description', 'equipment_type', 'manufacturer',
            'model_number', 'serial_number', 'purchase_date', 'purchase_cost',
            'status', 'current_location'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'equipment_type': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_cost': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'current_location': forms.TextInput(attrs={'class': 'form-control'})
        }

class EquipmentUsageForm(forms.ModelForm):
    class Meta:
        model = EquipmentUsage
        fields = [
            'equipment', 'project', 'task', 'start_date', 'end_date',
            'hours_used', 'notes'
        ]
        widgets = {
            'equipment': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'task': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hours_used': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.5'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be later than end date.")
        
        return cleaned_data

class EquipmentTransferForm(forms.ModelForm):
    class Meta:
        model = EquipmentTransfer
        fields = [
            'equipment', 'from_location', 'to_location', 'transfer_date',
            'reason', 'received_by', 'notes'
        ]
        widgets = {
            'equipment': forms.Select(attrs={'class': 'form-control'}),
            'from_location': forms.TextInput(attrs={'class': 'form-control'}),
            'to_location': forms.TextInput(attrs={'class': 'form-control'}),
            'transfer_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'received_by': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'capacity', 'manager', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SubcontractorForm(forms.ModelForm):
    class Meta:
        model = Subcontractor
        fields = ['name', 'contact_person', 'phone', 'email', 'address', 'specialization', 'status']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class CostCenterForm(forms.ModelForm):
    class Meta:
        model = CostCenter
        fields = ['name', 'description', 'budget', 'project']

class CostItemForm(forms.ModelForm):
    class Meta:
        model = CostItem
        fields = ['cost_center', 'description', 'cost_type', 'quantity', 'unit_price']
