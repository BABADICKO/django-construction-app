from django.db import models
from django.core import serializers
from .audit_models import AuditLog

class AuditLogMixin:
    def _get_changes(self, old_instance=None):
        if not old_instance:
            # For creation, all fields are considered changed
            changes = {}
            for field in self._meta.fields:
                if field.name != 'id' and hasattr(self, field.name):
                    val = getattr(self, field.name)
                    if isinstance(val, models.Model):
                        changes[field.name] = str(val)
                    else:
                        changes[field.name] = val
            return {'added': changes}
        
        # For updates, compare old and new values
        changes = {'changed': {}}
        for field in self._meta.fields:
            if field.name != 'id' and hasattr(self, field.name):
                old_val = getattr(old_instance, field.name)
                new_val = getattr(self, field.name)
                
                # Handle model instances
                if isinstance(old_val, models.Model):
                    old_val = str(old_val)
                if isinstance(new_val, models.Model):
                    new_val = str(new_val)
                
                if old_val != new_val:
                    changes['changed'][field.name] = {
                        'old': old_val,
                        'new': new_val
                    }
        return changes if changes['changed'] else None

    def log_action(self, action, user=None, request=None, changes=None):
        """
        Log an action performed on this model instance.
        """
        if not changes and action != 'DELETE':
            return  # No changes to log
            
        log_entry = AuditLog(
            user=user,
            action=action,
            model_name=self._meta.model_name,
            object_id=str(self.pk),
            object_repr=str(self),
            changes=changes
        )
        
        if request:
            log_entry.ip_address = self._get_client_ip(request)
            log_entry.user_agent = request.META.get('HTTP_USER_AGENT', '')
            
        log_entry.save()
        
    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
