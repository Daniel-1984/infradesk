from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ['department', 'role', 'phone', 'employee_id', 'bio']


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'get_full_name', 'email', 'get_role', 'get_department', 'is_active']
    list_filter = ['is_active', 'is_staff', 'profile__role', 'profile__department']

    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else '-'
    get_role.short_description = 'Perfil'

    def get_department(self, obj):
        return obj.profile.department if hasattr(obj, 'profile') else '-'
    get_department.short_description = 'Departamento'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
