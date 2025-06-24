from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('id','fullname', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('id', 'fullname', 'email')
    ordering = ('created_at'),
    fieldsets = (
        ('Credentials', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('fullname', 'phoneNo', 'profilePic')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'fullname', 'role', 'password1', 'password2'),
        }),
    )


admin.site.register(User, UserAdmin)