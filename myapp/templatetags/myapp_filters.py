from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def filter_status(tasks, status):
    """Filter tasks by status."""
    return [task for task in tasks if task.status == status]
