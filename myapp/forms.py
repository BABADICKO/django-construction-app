from django import forms
from .models import (
    Project, Material, MaterialCategory, MaterialSubcategory,
    MaterialTransaction, Task, Equipment, EquipmentUsage, EquipmentTransfer,
    Warehouse, Subcontractor, CostCenter, CostItem, EquipmentMaintenance,
    Milestone, BudgetItem, ResourceAllocation, TaskDependency
)

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'project', 'assigned_to',
            'status', 'priority', 'phase', 'progress',
            'start_date', 'due_date', 'estimated_hours'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # Add Bootstrap classes for select fields
        self.fields['project'].widget.attrs.update({'class': 'form-control form-select'})
        self.fields['assigned_to'].widget.attrs.update({'class': 'form-control form-select'})
        self.fields['status'].widget.attrs.update({'class': 'form-control form-select'})
        self.fields['priority'].widget.attrs.update({'class': 'form-control form-select'})
        self.fields['phase'].widget.attrs.update({'class': 'form-control form-select'})

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
        fields = ['name', 'description', 'start_date', 'end_date', 'status', 'budget', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the project'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Project budget'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional notes or comments'
            })
        }
        help_texts = {
            'name': 'A unique name for the project',
            'description': 'Provide a clear description of the project objectives',
            'start_date': 'Expected start date',
            'end_date': 'Expected completion date',
            'status': 'Current project status',
            'budget': 'Estimated project budget',
            'notes': 'Any additional information about the project'
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be later than end date.")
        
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
        fields = ['name', 'location', 'project', 'manager', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
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

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = EquipmentMaintenance
        fields = [
            'equipment', 'maintenance_type', 'description', 'scheduled_date',
            'completed_date', 'cost', 'notes'
        ]
        widgets = {
            'equipment': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def clean(self):
        cleaned_data = super().clean()
        scheduled_date = cleaned_data.get('scheduled_date')
        completed_date = cleaned_data.get('completed_date')
        
        if completed_date and scheduled_date and completed_date < scheduled_date:
            raise forms.ValidationError("Completion date cannot be earlier than scheduled date.")
        
        return cleaned_data

class StockTransferForm(forms.ModelForm):
    source_warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.filter(is_active=True),
        label='From Warehouse'
    )
    destination_warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.filter(is_active=True),
        label='To Warehouse'
    )
    
    class Meta:
        model = MaterialTransaction
        fields = ['material', 'quantity', 'notes']
        
    def clean(self):
        cleaned_data = super().clean()
        source_warehouse = cleaned_data.get('source_warehouse')
        destination_warehouse = cleaned_data.get('destination_warehouse')
        
        if source_warehouse and destination_warehouse:
            if source_warehouse == destination_warehouse:
                raise forms.ValidationError("Source and destination warehouses must be different")
                
        return cleaned_data


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['name', 'description', 'due_date']

class BudgetItemForm(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ['name', 'category', 'description', 'estimated_cost', 'actual_cost']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'estimated_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'actual_cost': forms.NumberInput(attrs={'step': '0.01'}),
        }

class ResourceAllocationForm(forms.ModelForm):
    class Meta:
        model = ResourceAllocation
        fields = ['resource_type', 'name', 'quantity', 'unit', 'start_date', 'end_date', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class TaskDependencyForm(forms.ModelForm):
    class Meta:
        model = TaskDependency
        fields = ['depends_on', 'dependency_type', 'lag_days']
        widgets = {
            'lag_days': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, task=None, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.fields['depends_on'].queryset = Task.objects.filter(project=project).exclude(id=task.id if task else None)

class ProjectPlanningForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'budget', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'budget': forms.NumberInput(attrs={'step': '0.01'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assigned_to', 'priority', 'phase',
            'start_date', 'due_date', 'estimated_hours'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'estimated_hours': forms.NumberInput(attrs={'step': '0.5', 'min': '0'}),
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.instance.project = project
