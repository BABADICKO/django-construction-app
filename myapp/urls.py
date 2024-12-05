from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    # Home URL
    path('', views.home, name='home'),
    
    # Audit Logs URL
    path('audit-logs/', views.audit_log_list, name='audit_log_list'),
    
    # Project URLs
    path('projects/dashboard/', views.project_dashboard, name='project_dashboard'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Task URLs
    path('tasks/dashboard/', views.task_dashboard, name='task_dashboard'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/import/', views.task_import, name='task_import'),
    
    # Equipment URLs
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/create/', views.equipment_create, name='equipment_create'),
    path('equipment/<int:pk>/edit/', views.equipment_edit, name='equipment_edit'),
    path('equipment/<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),
    path('equipment/import/', views.equipment_import, name='equipment_import'),
    path('equipment/usage/', views.equipment_usage, name='equipment_usage'),
    path('equipment/transfer/', views.equipment_transfer, name='equipment_transfer'),
    
    # Material URLs
    path('materials/dashboard/', views.material_dashboard, name='material_dashboard'),
    path('materials/', views.material_list, name='material_list'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/<int:pk>/edit/', views.material_edit, name='material_edit'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
    path('materials/import/', views.material_import, name='material_import'),
    path('materials/delivery/', views.record_delivery, name='materials_delivery'),
    path('materials/consumption/', views.record_consumption, name='materials_consumption'),
    path('materials/transactions/', views.material_transaction_list, name='material_transactions'),
    
    # Material Category URLs
    path('materials/categories/', views.category_list, name='category_list'),
    path('materials/categories/create/', views.category_create, name='category_create'),
    path('materials/categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('materials/categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Material Subcategory URLs
    path('materials/subcategories/create/', views.subcategory_create, name='subcategory_create'),
    path('materials/subcategories/<int:pk>/edit/', views.subcategory_edit, name='subcategory_edit'),
    path('materials/subcategories/<int:pk>/delete/', views.subcategory_delete, name='subcategory_delete'),
    path('materials/subcategories/by-category/<int:category_id>/', 
         views.get_subcategories, name='get_subcategories'),
    
    # Inventory URLs
    path('inventory/dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('inventory/warehouses/', views.warehouse_list, name='warehouse_list'),
    path('inventory/warehouses/create/', views.create_warehouse, name='warehouse_create'),
    path('inventory/warehouses/<int:pk>/edit/', views.edit_warehouse, name='warehouse_edit'),
    path('inventory/stock/transfer/', views.stock_transfer, name='stock_transfer'),
    path('inventory/transactions/delivery/', views.material_delivery, name='material_delivery'),
    path('inventory/transactions/consumption/', views.material_consumption, name='material_consumption'),
    
    # Subcontractor Management URLs
    path('subcontractors/dashboard/', views.subcontractor_dashboard, name='subcontractor_dashboard'),
    path('subcontractors/list/', views.subcontractor_list, name='subcontractor_list'),
    path('subcontractors/create/', views.subcontractor_create, name='subcontractor_create'),
    path('subcontractors/<int:pk>/edit/', views.subcontractor_edit, name='subcontractor_edit'),
    path('subcontractors/<int:pk>/delete/', views.subcontractor_delete, name='subcontractor_delete'),
    
    # Cost Management URLs
    path('costs/dashboard/', views.cost_dashboard, name='cost_dashboard'),
    path('costs/bom/', views.bom_list, name='bom_list'),
    path('costs/analysis/', views.cost_analysis, name='cost_analysis'),

    # Maintenance URLs
    path('maintenance/dashboard/', views.maintenance_dashboard, name='maintenance_dashboard'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/create/', views.maintenance_create, name='maintenance_create'),
    path('maintenance/<int:pk>/edit/', views.maintenance_edit, name='maintenance_edit'),
    path('maintenance/<int:pk>/delete/', views.maintenance_delete, name='maintenance_delete'),
    path('maintenance/calendar/', views.maintenance_calendar, name='maintenance_calendar'),
    
    # Milestone URLs
    path('projects/<int:project_id>/milestones/', views.milestone_list, name='milestone_list'),
    path('projects/<int:project_id>/milestones/add/', views.add_milestone, name='add_milestone'),
    path('milestones/<int:milestone_id>/complete/', views.mark_milestone_completed, name='mark_milestone_completed'),
    
    # User Management URLs
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/change-role/', views.change_user_role, name='change_user_role'),
    path('users/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    
    # Removed duplicate audit log URL
]
