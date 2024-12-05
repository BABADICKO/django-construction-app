from django.contrib import admin
from .models import (
    Project, Material, MaterialCategory, MaterialSubcategory,
    MaterialConsumption, MaterialDelivery
)

@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'parent', 'created_at']
    list_filter = ['parent']
    search_fields = ['name']
    ordering = ['name']

@admin.register(MaterialSubcategory)
class MaterialSubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'description', 'created_at']
    list_filter = ['category']
    search_fields = ['name', 'category__name']
    ordering = ['category__name', 'name']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'unit', 'current_stock', 'minimum_stock', 'unit_price']
    list_filter = ['category']
    search_fields = ['code', 'name', 'category__name']
    ordering = ['name']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'start_date', 'end_date', 'budget']
    list_filter = ['status', 'start_date']
    search_fields = ['name', 'description']
    date_hierarchy = 'start_date'

@admin.register(MaterialConsumption)
class MaterialConsumptionAdmin(admin.ModelAdmin):
    list_display = ['project', 'material', 'quantity', 'unit_price', 'total_cost', 'date', 'recorded_by']
    list_filter = ['project', 'material__category', 'date']
    search_fields = ['project__name', 'material__name', 'recorded_by__user__username']
    date_hierarchy = 'date'

@admin.register(MaterialDelivery)
class MaterialDeliveryAdmin(admin.ModelAdmin):
    list_display = ['project', 'material', 'quantity', 'unit_price', 'total_cost', 'supplier', 'delivery_date', 'received_by']
    list_filter = ['project', 'material__category', 'delivery_date']
    search_fields = ['project__name', 'material__name', 'supplier', 'received_by__user__username']
    date_hierarchy = 'delivery_date'
from django.contrib import admin
from .models import Milestone

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'due_date', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'due_date', 'project')
    search_fields = ('name', 'project__name')
