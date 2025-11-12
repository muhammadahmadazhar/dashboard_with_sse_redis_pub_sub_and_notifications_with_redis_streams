from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'staff_count']
    search_fields = ['name']

    def staff_count(self, obj):
        return obj.users.filter(user_type='staff').count()

    staff_count.short_description = 'Total Staff'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'organization', 'is_online', 'last_seen']
    list_filter = ['user_type', 'is_online', 'organization']
    search_fields = ['username', 'email']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'organization', 'is_online', 'last_seen')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'organization')
        }),
    )
