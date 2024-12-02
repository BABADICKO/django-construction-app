from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, Sum
from .models import (
    Project, Task, Material, MaterialCategory, MaterialSubcategory,
    MaterialTransaction, Equipment, EquipmentUsage, EquipmentTransfer,
    Warehouse, Subcontractor, SubcontractorAssignment, SubcontractorPayment,
    CostCenter, CostItem
)
from .forms import (
    TaskForm, MaterialTransactionForm, ProjectForm, TaskFormNew,
    EquipmentForm, EquipmentUsageForm, EquipmentTransferForm, MaterialForm,
    MaterialSubcategoryForm, WarehouseForm, SubcontractorForm,
    CostCenterForm, CostItemForm
)
from decimal import Decimal
import csv
from datetime import datetime

@login_required
def home(request):
    """Home page view showing dashboard with recent activities."""
    context = {
        'recent_tasks': Task.objects.select_related('project', 'assigned_to').order_by('-created_at')[:5],
        'recent_transactions': MaterialTransaction.objects.select_related('project', 'material').order_by('-created_at')[:5],
        'low_stock_materials': Material.objects.filter(current_stock__lte=F('minimum_stock'))[:5]
    }
    return render(request, 'myapp/home.html', context)

@login_required
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'myapp/project_list.html', {'projects': projects})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'Project created successfully.')
            return redirect('myapp:project_list')
    else:
        form = ProjectForm()
    return render(request, 'myapp/project_form.html', {'form': form, 'action': 'Create'})

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('myapp:project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'myapp/project_form.html', {'form': form, 'action': 'Edit'})

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('myapp:project_list')
    return render(request, 'myapp/project_confirm_delete.html', {'project': project})

@login_required
def material_list(request):
    # Get all materials with their categories and subcategories
    materials = Material.objects.select_related('category', 'subcategory').all()
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        materials = materials.filter(
            models.Q(name__icontains=search_query) |
            models.Q(code__icontains=search_query) |
            models.Q(category__name__icontains=search_query) |
            models.Q(subcategory__name__icontains=search_query)
        )
    
    # Handle category filtering
    category_id = request.GET.get('category')
    if category_id:
        materials = materials.filter(category_id=category_id)
    
    # Handle subcategory filtering
    subcategory_id = request.GET.get('subcategory')
    if subcategory_id:
        materials = materials.filter(subcategory_id=subcategory_id)
    
    # Handle stock level filtering
    stock_filter = request.GET.get('stock')
    if stock_filter == 'low':
        materials = materials.filter(current_stock__lte=F('minimum_stock'))
    elif stock_filter == 'out':
        materials = materials.filter(current_stock=0)
    
    # Get categories and subcategories for the filter dropdowns
    categories = MaterialCategory.objects.all()
    subcategories = MaterialSubcategory.objects.all()
    
    context = {
        'materials': materials,
        'categories': categories,
        'subcategories': subcategories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_subcategory': subcategory_id,
        'stock_filter': stock_filter
    }
    
    return render(request, 'myapp/materials/material_list.html', context)

@login_required
def material_create(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save()
            messages.success(request, 'Material created successfully.')
            return redirect('material_detail', material_id=material.id)
    else:
        form = MaterialForm()
    
    categories = MaterialCategory.objects.all()
    subcategories = MaterialSubcategory.objects.all()
    
    return render(request, 'myapp/materials/material_form.html', {
        'form': form,
        'categories': categories,
        'subcategories': subcategories,
    })

@login_required
def material_edit(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            material = form.save()
            messages.success(request, 'Material updated successfully.')
            return redirect('material_detail', material_id=material.id)
    else:
        form = MaterialForm(instance=material)
    
    categories = MaterialCategory.objects.all()
    subcategories = MaterialSubcategory.objects.filter(category=material.category)
    
    return render(request, 'myapp/materials/material_form.html', {
        'form': form,
        'categories': categories,
        'subcategories': subcategories,
    })

@login_required
def material_detail(request, material_id):
    material = get_object_or_404(Material.objects.select_related('category'), id=material_id)
    
    # Get recent transactions
    recent_deliveries = MaterialDelivery.objects.filter(material=material).order_by('-delivery_date')[:5]
    recent_consumptions = MaterialConsumption.objects.filter(material=material).order_by('-date')[:5]
    
    # Calculate statistics
    total_delivered = MaterialDelivery.objects.filter(material=material).aggregate(
        total=Coalesce(Sum('quantity'), Value(0))
    )['total']
    
    total_consumed = MaterialConsumption.objects.filter(material=material).aggregate(
        total=Coalesce(Sum('quantity'), Value(0))
    )['total']
    
    # Calculate average price from recent deliveries
    recent_prices = MaterialDelivery.objects.filter(material=material).order_by('-delivery_date')[:5]
    avg_price = recent_prices.aggregate(avg=models.Avg('unit_price'))['avg'] or material.unit_price
    
    # Get projects using this material
    projects_using = Project.objects.filter(
        id__in=MaterialConsumption.objects.filter(material=material).values_list('project_id', flat=True)
    ).distinct()
    
    context = {
        'material': material,
        'recent_deliveries': recent_deliveries,
        'recent_consumptions': recent_consumptions,
        'total_delivered': total_delivered,
        'total_consumed': total_consumed,
        'avg_price': avg_price,
        'projects_using': projects_using,
        'stock_status': 'Low' if material.current_stock <= material.minimum_stock else 'Normal',
        'stock_alert': material.current_stock <= material.minimum_stock
    }
    
    return render(request, 'myapp/materials/material_detail.html', context)

@login_required
def material_delete(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    
    if request.method == 'POST':
        try:
            material_name = material.name
            material.delete()
            messages.success(request, f'Material "{material_name}" deleted successfully!')
            return redirect('material_list')
        except Exception as e:
            messages.error(request, f'Error deleting material: {str(e)}')
            return redirect('material_detail', material_id=material_id)
    
    return render(request, 'myapp/materials/material_confirm_delete.html', {'material': material})

@login_required
def record_consumption(request):
    if request.method == 'POST':
        try:
            material_id = request.POST.get('material')
            project_id = request.POST.get('project')
            quantity = request.POST.get('quantity')
            unit_price = request.POST.get('unit_price')
            date = request.POST.get('date')
            notes = request.POST.get('notes')
            
            # Get the material
            material = Material.objects.get(id=material_id)
            
            # Check if we have enough stock
            if material.current_stock < Decimal(quantity):
                messages.error(request, f'Not enough stock! Available: {material.current_stock} {material.unit}')
                return redirect('record_consumption')
            
            # Create consumption record
            consumption = MaterialConsumption.objects.create(
                material_id=material_id,
                project_id=project_id,
                quantity=quantity,
                unit_price=unit_price,
                date=date,
                notes=notes,
                recorded_by=request.user.customuser
            )
            
            # Update material stock
            material.current_stock -= Decimal(quantity)
            material.save()
            
            messages.success(request, 'Consumption recorded successfully!')
            return redirect('material_detail', material_id=material_id)
            
        except Exception as e:
            messages.error(request, f'Error recording consumption: {str(e)}')
            return redirect('record_consumption')
    
    # Get active projects and materials for the form
    projects = Project.objects.filter(status='ONGOING')
    materials = Material.objects.all()
    
    return render(request, 'myapp/materials/consumption_form.html', {
        'projects': projects,
        'materials': materials
    })

@login_required
def record_delivery(request):
    if request.method == 'POST':
        try:
            material_id = request.POST.get('material')
            project_id = request.POST.get('project')
            quantity = request.POST.get('quantity')
            unit_price = request.POST.get('unit_price')
            supplier = request.POST.get('supplier')
            delivery_date = request.POST.get('delivery_date')
            invoice_number = request.POST.get('invoice_number')
            notes = request.POST.get('notes')
            
            # Create delivery record
            delivery = MaterialDelivery.objects.create(
                material_id=material_id,
                project_id=project_id,
                quantity=quantity,
                unit_price=unit_price,
                supplier=supplier,
                delivery_date=delivery_date,
                invoice_number=invoice_number,
                notes=notes,
                received_by=request.user.customuser
            )
            
            # Update material stock and price
            material = Material.objects.get(id=material_id)
            material.current_stock += Decimal(quantity)
            material.unit_price = unit_price  # Update to latest price
            material.save()
            
            messages.success(request, 'Delivery recorded successfully!')
            return redirect('material_detail', material_id=material_id)
            
        except Exception as e:
            messages.error(request, f'Error recording delivery: {str(e)}')
            return redirect('record_delivery')
    
    # Get active projects and materials for the form
    projects = Project.objects.filter(status='ONGOING')
    materials = Material.objects.all()
    
    return render(request, 'myapp/materials/delivery_form.html', {
        'projects': projects,
        'materials': materials
    })

# Category Management Views
@login_required
def category_list(request):
    categories = MaterialCategory.objects.all()
    return render(request, 'myapp/materials/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            parent_id = request.POST.get('parent')
            
            category = MaterialCategory.objects.create(
                name=name,
                description=description,
                parent_id=parent_id if parent_id else None
            )
            
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('category_list')
            
        except Exception as e:
            messages.error(request, f'Error creating category: {str(e)}')
    
    # Get all categories for parent selection
    categories = MaterialCategory.objects.all()
    return render(request, 'myapp/materials/category_form.html', {'categories': categories})

@login_required
def category_edit(request, category_id):
    category = get_object_or_404(MaterialCategory, id=category_id)
    
    if request.method == 'POST':
        try:
            category.name = request.POST.get('name')
            category.description = request.POST.get('description')
            parent_id = request.POST.get('parent')
            category.parent_id = parent_id if parent_id else None
            category.save()
            
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('category_list')
            
        except Exception as e:
            messages.error(request, f'Error updating category: {str(e)}')
    
    # Get all categories for parent selection, excluding self and children
    available_parents = MaterialCategory.objects.exclude(
        models.Q(id=category_id) |
        models.Q(parent_id=category_id)
    )
    
    return render(request, 'myapp/materials/category_form.html', {
        'category': category,
        'categories': available_parents
    })

@login_required
def category_delete(request, category_id):
    category = get_object_or_404(MaterialCategory, id=category_id)
    
    if request.method == 'POST':
        try:
            category_name = category.name
            category.delete()
            messages.success(request, f'Category "{category_name}" deleted successfully!')
            return redirect('category_list')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
    
    return render(request, 'myapp/materials/category_confirm_delete.html', {'category': category})

# Subcategory Management Views
@login_required
def subcategory_create(request):
    if request.method == 'POST':
        form = MaterialSubcategoryForm(request.POST)
        if form.is_valid():
            subcategory = form.save()
            messages.success(request, 'Material subcategory created successfully.')
            return redirect('myapp:category_list')
    else:
        form = MaterialSubcategoryForm()
    
    return render(request, 'myapp/subcategory_form.html', {'form': form, 'action': 'Create'})

@login_required
def subcategory_edit(request, pk):
    subcategory = get_object_or_404(MaterialSubcategory, pk=pk)
    if request.method == 'POST':
        form = MaterialSubcategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material subcategory updated successfully.')
            return redirect('myapp:category_list')
    else:
        form = MaterialSubcategoryForm(instance=subcategory)
    
    return render(request, 'myapp/subcategory_form.html', {'form': form, 'action': 'Edit'})

@login_required
def subcategory_delete(request, pk):
    subcategory = get_object_or_404(MaterialSubcategory, pk=pk)
    if request.method == 'POST':
        subcategory.delete()
        messages.success(request, 'Material subcategory deleted successfully.')
        return redirect('myapp:category_list')
    
    return render(request, 'myapp/subcategory_confirm_delete.html', {'subcategory': subcategory})

@login_required
def get_subcategories(request, category_id):
    subcategories = MaterialSubcategory.objects.filter(category_id=category_id)
    data = [{'id': sub.id, 'name': sub.name} for sub in subcategories]
    return JsonResponse(data, safe=False)

# API endpoint for dynamic subcategory loading
@login_required
def get_subcategories(request, category_id):
    subcategories = MaterialSubcategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)

@login_required
def all_projects(request):
    projects = Project.objects.select_related('manager')
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        projects = projects.filter(
            models.Q(name__icontains=search_query) |
            models.Q(code__icontains=search_query) |
            models.Q(location__icontains=search_query)
        )
    
    # Handle status filtering
    status = request.GET.get('status')
    if status:
        projects = projects.filter(status=status.upper())
    
    # Handle sorting
    sort_by = request.GET.get('sort')
    if sort_by:
        if sort_by == 'deadline':
            projects = projects.order_by('end_date')
        elif sort_by == 'budget':
            projects = projects.order_by('-total_budget')
        elif sort_by == 'name':
            projects = projects.order_by('name')
        elif sort_by == 'progress':
            projects = projects.order_by('-progress')
    else:
        # Default sort by creation date
        projects = projects.order_by('-created_at')
    
    # Calculate progress for each project
    for project in projects:
        # You can customize this calculation based on your needs
        if project.status == 'COMPLETED':
            project.progress = 100
        elif project.status == 'NOT_STARTED':
            project.progress = 0
        else:
            # Calculate based on timeline
            total_days = (project.end_date - project.start_date).days
            days_passed = (timezone.now().date() - project.start_date).days
            project.progress = min(100, max(0, int((days_passed / total_days) * 100)))
        
        # Add status color for badges
        project.status_color = {
            'NOT_STARTED': 'info',
            'ONGOING': 'primary',
            'COMPLETED': 'success',
            'ON_HOLD': 'warning',
            'CANCELLED': 'danger'
        }.get(project.status, 'secondary')
    
    return render(request, 'myapp/project_list.html', {'projects': projects})

@login_required
def create_project(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        code = request.POST.get('code')
        location = request.POST.get('location')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        total_budget = request.POST.get('total_budget')
        status = request.POST.get('status')
        
        try:
            # Create new project
            project = Project.objects.create(
                name=name,
                code=code,
                location=location,
                description=description,
                start_date=start_date,
                end_date=end_date,
                total_budget=total_budget,
                status=status,
                manager=request.user
            )
            messages.success(request, 'Project created successfully!')
            return redirect('project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
            return redirect('create_project')
    
    return render(request, 'myapp/create_project.html')

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project.objects.select_related('manager'), id=project_id)
    
    # Calculate days remaining
    today = timezone.now().date()
    days_remaining = (project.end_date - today).days if project.end_date > today else 0
    
    # Calculate budget used (you'll need to implement actual budget tracking)
    budget_used = 45  # Example value, replace with actual calculation
    
    # Get material count for this project
    material_count = MaterialConsumption.objects.filter(project=project).count()
    
    # Example data for team members (implement your own team member model)
    team_members_count = 5  # Replace with actual count
    
    # Example data for documents (implement your own document model)
    document_count = 3  # Replace with actual count
    
    # Example data for issues (implement your own issue tracking)
    open_issues_count = 2  # Replace with actual count
    
    # Example data for tasks (implement your own task model)
    completed_tasks = 8  # Replace with actual count
    total_tasks = 12  # Replace with actual count
    
    # Get recent activities (implement your own activity tracking)
    recent_activities = [
        {
            'title': 'Material Delivered',
            'description': '20 tons of cement delivered to site',
            'timestamp': timezone.now() - timedelta(hours=2)
        },
        {
            'title': 'Task Completed',
            'description': 'Foundation work completed',
            'timestamp': timezone.now() - timedelta(days=1)
        },
        {
            'title': 'New Team Member',
            'description': 'John Doe joined the project',
            'timestamp': timezone.now() - timedelta(days=2)
        }
    ]  # Replace with actual activities
    
    context = {
        'project': project,
        'days_remaining': days_remaining,
        'budget_used': budget_used,
        'material_count': material_count,
        'team_members_count': team_members_count,
        'document_count': document_count,
        'open_issues_count': open_issues_count,
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'recent_activities': recent_activities
    }
    
    return render(request, 'myapp/project_detail.html', context)

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        # Get form data
        project.name = request.POST.get('name')
        project.code = request.POST.get('code')
        project.location = request.POST.get('location')
        project.description = request.POST.get('description')
        project.start_date = request.POST.get('start_date')
        project.end_date = request.POST.get('end_date')
        project.total_budget = request.POST.get('total_budget')
        project.status = request.POST.get('status')
        
        try:
            project.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'Error updating project: {str(e)}')
    
    return render(request, 'myapp/edit_project.html', {'project': project})

@login_required
def project_dashboard(request):
    projects = Project.objects.all()
    return render(request, 'myapp/project_dashboard.html', {'projects': projects})

@login_required
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'myapp/project_list.html', {'projects': projects})

@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, 'Project created successfully.')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'myapp/add_project.html', {'form': form})

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'myapp/edit_project.html', {'form': form, 'project': project})

@login_required
def task_dashboard(request):
    tasks = Task.objects.all()
    return render(request, 'myapp/task_dashboard.html', {'tasks': tasks})

@login_required
def task_list(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project)
    return render(request, 'myapp/task_list.html', {'tasks': tasks, 'project': project})

@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task created successfully.')
            return redirect('task_list', project_id=task.project.id)
    else:
        form = TaskForm()
    return render(request, 'myapp/add_task.html', {'form': form})

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('task_list', project_id=task.project.id)
    else:
        form = TaskForm(instance=task)
    return render(request, 'myapp/edit_task.html', {'form': form, 'task': task})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskFormNew(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user.customuser
            task.save()
            messages.success(request, 'Task created successfully.')
            return redirect('myapp:task_list')
    else:
        form = TaskFormNew()
    return render(request, 'myapp/task_form.html', {'form': form, 'action': 'Create'})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskFormNew(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('myapp:task_list')
    else:
        form = TaskFormNew(instance=task)
    return render(request, 'myapp/task_form.html', {'form': form, 'action': 'Edit', 'task': task})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('myapp:task_list')
    return render(request, 'myapp/task_confirm_delete.html', {'task': task})

@login_required
def task_import(request):
    if request.method == 'POST' and request.FILES.get('task_file'):
        file = request.FILES['task_file']
        try:
            # Read the CSV file
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                # Create task from CSV data
                task = Task(
                    title=row['title'],
                    description=row.get('description', ''),
                    project_id=row['project_id'],
                    assigned_to_id=row['assigned_to_id'],
                    status=row.get('status', 'NOT_STARTED'),
                    priority=row.get('priority', 'MEDIUM'),
                    progress=int(row.get('progress', 0)),
                    start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
                    due_date=datetime.strptime(row['due_date'], '%Y-%m-%d').date(),
                    created_by=request.user.customuser
                )
                task.save()
            
            messages.success(request, 'Tasks imported successfully.')
            return redirect('myapp:task_list')
        except Exception as e:
            messages.error(request, f'Error importing tasks: {str(e)}')
    
    return render(request, 'myapp/task_import.html')

@login_required
def equipment_list(request):
    equipment = Equipment.objects.all()
    return render(request, 'myapp/equipment_list.html', {'equipment': equipment})

@login_required
def equipment_create(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            equipment = form.save()
            messages.success(request, 'Equipment created successfully.')
            return redirect('myapp:equipment_list')
    else:
        form = EquipmentForm()
    return render(request, 'myapp/equipment_form.html', {'form': form, 'action': 'Create'})

@login_required
def equipment_edit(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            equipment = form.save()
            messages.success(request, 'Equipment updated successfully.')
            return redirect('myapp:equipment_list')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'myapp/equipment_form.html', {'form': form, 'action': 'Edit', 'equipment': equipment})

@login_required
def equipment_delete(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        equipment.delete()
        messages.success(request, 'Equipment deleted successfully.')
        return redirect('myapp:equipment_list')
    return render(request, 'myapp/equipment_confirm_delete.html', {'equipment': equipment})

@login_required
def equipment_import(request):
    if request.method == 'POST' and request.FILES.get('equipment_file'):
        file = request.FILES['equipment_file']
        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                equipment = Equipment(
                    name=row['name'],
                    code=row['code'],
                    description=row.get('description', ''),
                    equipment_type=row['equipment_type'],
                    manufacturer=row['manufacturer'],
                    model_number=row['model_number'],
                    serial_number=row['serial_number'],
                    purchase_date=datetime.strptime(row['purchase_date'], '%Y-%m-%d').date(),
                    purchase_cost=Decimal(row['purchase_cost']),
                    status=row.get('status', 'AVAILABLE'),
                    current_location=row['current_location']
                )
                equipment.save()
            
            messages.success(request, 'Equipment imported successfully.')
            return redirect('myapp:equipment_list')
        except Exception as e:
            messages.error(request, f'Error importing equipment: {str(e)}')
    
    return render(request, 'myapp/equipment_import.html')

@login_required
def equipment_usage(request):
    if request.method == 'POST':
        form = EquipmentUsageForm(request.POST)
        if form.is_valid():
            usage = form.save(commit=False)
            usage.operator = request.user.customuser
            usage.save()
            messages.success(request, 'Equipment usage recorded successfully.')
            return redirect('myapp:equipment_list')
    else:
        form = EquipmentUsageForm()
    return render(request, 'myapp/equipment_usage_form.html', {'form': form})

@login_required
def equipment_transfer(request):
    if request.method == 'POST':
        form = EquipmentTransferForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.transferred_by = request.user.customuser
            transfer.save()
            
            equipment = transfer.equipment
            equipment.current_location = transfer.to_location
            equipment.save()
            
            messages.success(request, 'Equipment transfer recorded successfully.')
            return redirect('myapp:equipment_list')
    else:
        form = EquipmentTransferForm()
    return render(request, 'myapp/equipment_transfer_form.html', {'form': form})

@login_required
def material_dashboard(request):
    materials = Material.objects.select_related('category', 'subcategory').all()
    low_stock_materials = materials.filter(current_stock__lte=F('minimum_stock'))
    out_of_stock_materials = materials.filter(current_stock=0)
    
    # Get recent transactions
    recent_transactions = MaterialTransaction.objects.select_related(
        'material', 'project'
    ).order_by('-created_at')[:10]
    
    context = {
        'total_materials': materials.count(),
        'low_stock_count': low_stock_materials.count(),
        'out_of_stock_count': out_of_stock_materials.count(),
        'recent_transactions': recent_transactions,
        'low_stock_materials': low_stock_materials[:5],
        'out_of_stock_materials': out_of_stock_materials[:5]
    }
    return render(request, 'myapp/material_dashboard.html', context)

@login_required
def material_create(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save()
            messages.success(request, 'Material created successfully.')
            return redirect('myapp:material_list')
    else:
        form = MaterialForm()
    return render(request, 'myapp/material_form.html', {'form': form, 'action': 'Create'})

@login_required
def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            material = form.save()
            messages.success(request, 'Material updated successfully.')
            return redirect('myapp:material_list')
    else:
        form = MaterialForm(instance=material)
    return render(request, 'myapp/material_form.html', {'form': form, 'action': 'Edit', 'material': material})

@login_required
def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material deleted successfully.')
        return redirect('myapp:material_list')
    return render(request, 'myapp/material_confirm_delete.html', {'material': material})

@login_required
def material_import(request):
    if request.method == 'POST' and request.FILES.get('material_file'):
        file = request.FILES['material_file']
        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                material = Material(
                    name=row['name'],
                    code=row['code'],
                    category_id=row['category_id'],
                    subcategory_id=row.get('subcategory_id'),
                    description=row.get('description', ''),
                    unit=row['unit'],
                    unit_price=Decimal(row['unit_price']),
                    minimum_stock=Decimal(row.get('minimum_stock', '0')),
                    current_stock=Decimal(row.get('current_stock', '0'))
                )
                material.save()
            
            messages.success(request, 'Materials imported successfully.')
            return redirect('myapp:material_list')
        except Exception as e:
            messages.error(request, f'Error importing materials: {str(e)}')
    
    return render(request, 'myapp/material_import.html')

@login_required
def inventory_dashboard(request):
    # Get summary statistics
    total_materials = Material.objects.count()
    low_stock_materials = Material.objects.filter(current_stock__lte=F('minimum_stock')).count()
    recent_transactions = MaterialTransaction.objects.select_related(
        'material', 'project'
    ).order_by('-date')[:10]
    
    context = {
        'total_materials': total_materials,
        'low_stock_materials': low_stock_materials,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'myapp/inventory/dashboard.html', context)

@login_required
def warehouse_create(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, 'Warehouse created successfully.')
            return redirect('myapp:inventory_dashboard')
    else:
        form = WarehouseForm()
    
    return render(request, 'myapp/inventory/warehouse_form.html', {'form': form, 'action': 'Create'})

@login_required
def stock_entry(request):
    if request.method == 'POST':
        form = MaterialTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = 'RECEIPT'
            transaction.save()
            
            # Update material stock
            material = transaction.material
            material.current_stock += transaction.quantity
            material.save()
            
            messages.success(request, 'Stock entry recorded successfully.')
            return redirect('myapp:inventory_dashboard')
    else:
        form = MaterialTransactionForm()
    
    return render(request, 'myapp/inventory/stock_entry_form.html', {'form': form})

@login_required
def material_transaction(request):
    if request.method == 'POST':
        form = MaterialTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            material = transaction.material
            
            # Update material stock based on transaction type
            if transaction.transaction_type == 'CONSUMPTION':
                if transaction.quantity > material.current_stock:
                    messages.error(request, f'Insufficient stock. Available: {material.current_stock} {material.unit}')
                    return render(request, 'myapp/inventory/transaction_form.html', {'form': form})
                material.current_stock -= transaction.quantity
            else:  # RECEIPT
                material.current_stock += transaction.quantity
            
            material.save()
            transaction.save()
            messages.success(request, 'Transaction recorded successfully.')
            return redirect('myapp:inventory_dashboard')
    else:
        form = MaterialTransactionForm()
    
    return render(request, 'myapp/inventory/transaction_form.html', {'form': form})

@login_required
def subcontractor_dashboard(request):
    """Dashboard view for subcontractor management."""
    context = {
        'active_subcontractors': Subcontractor.objects.filter(status='active').count(),
        'total_payments': SubcontractorPayment.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'recent_assignments': SubcontractorAssignment.objects.select_related('subcontractor', 'project').order_by('-created_at')[:5],
        'recent_payments': SubcontractorPayment.objects.select_related('subcontractor').order_by('-payment_date')[:5]
    }
    return render(request, 'myapp/subcontractors/dashboard.html', context)

@login_required
def subcontractor_list(request):
    """List view for all subcontractors."""
    subcontractors = Subcontractor.objects.all().order_by('name')
    return render(request, 'myapp/subcontractors/list.html', {'subcontractors': subcontractors})

@login_required
def subcontractor_create(request):
    """Create a new subcontractor."""
    if request.method == 'POST':
        form = SubcontractorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcontractor created successfully.')
            return redirect('myapp:subcontractor_list')
    else:
        form = SubcontractorForm()
    return render(request, 'myapp/subcontractors/form.html', {'form': form, 'action': 'Create'})

@login_required
def subcontractor_edit(request, pk):
    """Edit an existing subcontractor."""
    subcontractor = get_object_or_404(Subcontractor, pk=pk)
    if request.method == 'POST':
        form = SubcontractorForm(request.POST, instance=subcontractor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcontractor updated successfully.')
            return redirect('myapp:subcontractor_list')
    else:
        form = SubcontractorForm(instance=subcontractor)
    return render(request, 'myapp/subcontractors/form.html', {'form': form, 'action': 'Edit'})

@login_required
def subcontractor_delete(request, pk):
    """Delete a subcontractor."""
    subcontractor = get_object_or_404(Subcontractor, pk=pk)
    if request.method == 'POST':
        subcontractor.delete()
        messages.success(request, 'Subcontractor deleted successfully.')
        return redirect('myapp:subcontractor_list')
    return render(request, 'myapp/subcontractors/confirm_delete.html', {'subcontractor': subcontractor})

@login_required
def cost_dashboard(request):
    """Dashboard view for cost management."""
    context = {
        'total_budget': CostCenter.objects.aggregate(total=Sum('budget'))['total'] or 0,
        'total_spent': CostItem.objects.aggregate(total=Sum(F('quantity') * F('unit_price')))['total'] or 0,
        'recent_costs': CostItem.objects.select_related('cost_center').order_by('-created_at')[:5],
        'cost_centers': CostCenter.objects.annotate(
            spent=Sum(F('cost_items__quantity') * F('cost_items__unit_price')),
            remaining=F('budget') - Sum(F('cost_items__quantity') * F('cost_items__unit_price'))
        )[:5]
    }
    return render(request, 'myapp/costs/dashboard.html', context)

@login_required
def bom_list(request):
    """View for Bill of Materials list."""
    cost_centers = CostCenter.objects.prefetch_related('cost_items').all()
    return render(request, 'myapp/costs/bom_list.html', {'cost_centers': cost_centers})

@login_required
def cost_analysis(request):
    """View for cost analysis and reports."""
    cost_by_type = CostItem.objects.values('cost_type').annotate(
        total=Sum(F('quantity') * F('unit_price'))
    ).order_by('-total')
    
    cost_items = CostItem.objects.select_related('cost_center').order_by('-created_at')[:10]
    
    context = {
        'cost_by_type': cost_by_type,
        'cost_items': cost_items
    }
    return render(request, 'myapp/costs/analysis.html', context)