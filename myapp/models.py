from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone
from .mixins import AuditLogMixin

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class CustomUser(AuditLogMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    phone = models.CharField(max_length=20)
    employee_id = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.department.name}"
        
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.user.groups.filter(name=role_name).exists()
    
    def get_role(self):
        """Get the user's current role"""
        group = self.user.groups.first()
        return group.name if group else None
    
    def has_perm(self, perm):
        """Check if user has a specific permission"""
        return self.user.has_perm(perm)

class Project(AuditLogMixin, models.Model):
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('ON_HOLD', 'On Hold'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='managed_projects', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

    def get_total_planned_budget(self):
        return self.budget_items.aggregate(
            total=models.Sum('estimated_cost')
        )['total'] or 0

    def get_total_actual_cost(self):
        return self.budget_items.aggregate(
            total=models.Sum('actual_cost')
        )['total'] or 0

    def get_budget_variance(self):
        return self.get_total_actual_cost() - self.get_total_planned_budget()

    def is_over_budget(self):
        return self.get_total_actual_cost() > self.get_total_planned_budget()

class MaterialCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Material Categories"
        ordering = ['name']

class MaterialSubcategory(models.Model):
    category = models.ForeignKey(MaterialCategory, on_delete=models.CASCADE, related_name='material_subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    class Meta:
        verbose_name_plural = "Material Subcategories"
        ordering = ['category__name', 'name']

class Material(AuditLogMixin, models.Model):
    UNIT_CHOICES = [
        ('KG', 'Kilogram'),
        ('L', 'Liter'),
        ('M', 'Meter'),
        ('M2', 'Square Meter'),
        ('M3', 'Cubic Meter'),
        ('UNIT', 'Unit'),
        ('BAG', 'Bag'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(MaterialCategory, on_delete=models.PROTECT)
    subcategory = models.ForeignKey(MaterialSubcategory, on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['category', 'subcategory', 'name']

class Task(AuditLogMixin, models.Model):
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent')
    ]

    PHASE_CHOICES = [
        ('PLANNING', 'Planning'),
        ('EXECUTION', 'Execution')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='assigned_tasks')
    created_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='created_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='EXECUTION')
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    start_date = models.DateField()
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_dependent_tasks(self):
        return Task.objects.filter(dependencies__depends_on=self)

    def get_prerequisite_tasks(self):
        return Task.objects.filter(dependents__task=self)

    class Meta:
        ordering = ['-priority', 'due_date']

    def save(self, *args, **kwargs):
        if self.status == 'COMPLETED' and not self.completed_date:
            self.completed_date = timezone.now().date()
            self.progress = 100
        elif self.status != 'COMPLETED':
            self.completed_date = None
        super().save(*args, **kwargs)
        # Update project progress
        self.project.update_progress()

class MaterialTransaction(AuditLogMixin, models.Model):
    TRANSACTION_TYPES = [
        ('DELIVERY', 'Delivery'),
        ('CONSUMPTION', 'Consumption')
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='material_transactions', null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='transactions')
    warehouse = models.ForeignKey('Warehouse', on_delete=models.PROTECT, related_name='transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date = models.DateField(default=timezone.now)
    supplier = models.CharField(max_length=200, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.material.name} ({self.quantity} {self.material.unit})"

    def total_price(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now().date()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Reverse the stock update when deleting a transaction
        if self.transaction_type == 'DELIVERY':
            self.material.current_stock -= self.quantity
        else:  # CONSUMPTION
            self.material.current_stock += abs(self.quantity)
        self.material.save()
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-date', '-created_at']

class MaterialConsumption(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()  # Keep original field name
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.material.name} - {self.quantity} {self.material.unit}"

    @property
    def total_cost(self):
        return self.quantity * self.unit_price

    @property
    def consumption_date(self):
        return self.date  # For admin display

    class Meta:
        ordering = ['-date']

class MaterialDelivery(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=200)
    delivery_date = models.DateField()
    received_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    invoice_number = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.material.name} - {self.quantity} {self.material.unit}"

    @property
    def total_cost(self):
        return self.quantity * self.unit_price

    class Meta:
        verbose_name_plural = "Material Deliveries"
        ordering = ['-delivery_date']

class Equipment(AuditLogMixin, models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('IN_USE', 'In Use'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('REPAIR', 'Under Repair'),
        ('RETIRED', 'Retired')
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    equipment_type = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    current_location = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['name']

class EquipmentMaintenance(models.Model):
    MAINTENANCE_TYPE_CHOICES = [
        ('PREVENTIVE', 'Preventive Maintenance'),
        ('CORRECTIVE', 'Corrective Maintenance'),
        ('INSPECTION', 'Inspection'),
        ('CALIBRATION', 'Calibration')
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=15, decimal_places=2)
    performed_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.equipment.name} - {self.maintenance_type} - {self.scheduled_date}"

    class Meta:
        ordering = ['-scheduled_date']

class EquipmentUsage(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='usage_records')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='equipment_usage')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='equipment_usage', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    hours_used = models.DecimalField(max_digits=10, decimal_places=2)
    operator = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='equipment_operations')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.equipment.name} - {self.project.name}"

    class Meta:
        ordering = ['-start_date']

class EquipmentTransfer(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='transfers')
    from_location = models.CharField(max_length=200)
    to_location = models.CharField(max_length=200)
    transfer_date = models.DateField()
    reason = models.TextField()
    transferred_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='equipment_transfers')
    received_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='equipment_receipts')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.equipment.name} - {self.from_location} to {self.to_location}"

    class Meta:
        ordering = ['-transfer_date']

class Warehouse(AuditLogMixin, models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='warehouses', null=True, blank=True)  # Making it nullable temporarily
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.project.name if self.project else 'No Project'}"

    class Meta:
        ordering = ['name']

class Subcontractor(AuditLogMixin, models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('BLACKLISTED', 'Blacklisted')
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    specialization = models.CharField(max_length=200)
    tax_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(5)])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['name']

class SubcontractorAssignment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]
    
    subcontractor = models.ForeignKey(Subcontractor, on_delete=models.CASCADE, related_name='assignments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='subcontractor_assignments')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subcontractor_assignments', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    contract_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    scope_of_work = models.TextField()
    terms_and_conditions = models.TextField()
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='subcontractor_assignments')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subcontractor.name} - {self.project.name}"

    class Meta:
        ordering = ['-start_date']

class SubcontractorPayment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('ADVANCE', 'Advance Payment'),
        ('PROGRESS', 'Progress Payment'),
        ('FINAL', 'Final Payment')
    ]
    
    assignment = models.ForeignKey(SubcontractorAssignment, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
    invoice_number = models.CharField(max_length=100)
    description = models.TextField()
    approved_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='approved_payments')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.assignment.subcontractor.name} - {self.payment_type} - {self.payment_date}"

    class Meta:
        ordering = ['-payment_date']

class CostCenter(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='cost_centers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.project.name}"

    class Meta:
        ordering = ['name']

class CostItem(models.Model):
    COST_TYPE_CHOICES = [
        ('material', 'Material'),
        ('labor', 'Labor'),
        ('equipment', 'Equipment'),
        ('subcontractor', 'Subcontractor'),
        ('overhead', 'Overhead'),
        ('other', 'Other'),
    ]

    cost_center = models.ForeignKey(CostCenter, on_delete=models.CASCADE, related_name='cost_items')
    description = models.CharField(max_length=200)
    cost_type = models.CharField(max_length=20, choices=COST_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_cost(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} - {self.cost_type}"

    class Meta:
        ordering = ['-created_at']

class BudgetItem(models.Model):
    CATEGORY_CHOICES = [
        ('MATERIAL', 'Material'),
        ('LABOR', 'Labor'),
        ('EQUIPMENT', 'Equipment'),
        ('SUBCONTRACTOR', 'Subcontractor'),
        ('OVERHEAD', 'Overhead'),
        ('OTHER', 'Other'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='budget_items')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.project.name}"

    def get_variance(self):
        if self.actual_cost:
            return self.actual_cost - self.estimated_cost
        return None

    def is_over_budget(self):
        if self.actual_cost:
            return self.actual_cost > self.estimated_cost
        return False

    class Meta:
        ordering = ['category', 'name']

class ResourceAllocation(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('MATERIAL', 'Material'),
        ('EQUIPMENT', 'Equipment'),
        ('LABOR', 'Labor'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='resource_allocations')
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.project.name}"

    class Meta:
        ordering = ['resource_type', 'start_date']

class TaskDependency(models.Model):
    DEPENDENCY_TYPE_CHOICES = [
        ('FINISH_TO_START', 'Finish to Start'),
        ('START_TO_START', 'Start to Start'),
        ('FINISH_TO_FINISH', 'Finish to Finish'),
        ('START_TO_FINISH', 'Start to Finish'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependencies')
    depends_on = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependents')
    dependency_type = models.CharField(max_length=20, choices=DEPENDENCY_TYPE_CHOICES, default='FINISH_TO_START')
    lag_days = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task.title} depends on {self.depends_on.title}"

    class Meta:
        ordering = ['task', 'depends_on']
        verbose_name_plural = 'Task Dependencies'

class Milestone(AuditLogMixin, models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(
        'Project', on_delete=models.CASCADE, related_name='milestones'
    )
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateField(null=True, blank=True)

    def mark_as_completed(self):
        self.is_completed = True
        self.completed_at = timezone.now().date()
        self.save()

    def __str__(self):
        return f"{self.name} (Due: {self.due_date})"

    class Meta:
        ordering = ['due_date']
        verbose_name = "Milestone"
        verbose_name_plural = "Milestones"
