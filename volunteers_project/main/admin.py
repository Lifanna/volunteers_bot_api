from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from . import models


class CustomUserAdmin(UserAdmin):
    """Регистрация модели CustomUser в админ панели"""
    fieldsets = (
        (None, {'fields': ('password',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_superuser', 'is_admin', 'groups', 'user_permissions',),
        }),
        ('Important dates', {'fields': ('last_login',)}),
    )

    list_display = ('__str__', 'phone_number',)

    list_filter = ('phone_number', 'first_name', 'last_name',)

    search_fields = ('phone_number', 'first_name', 'last_name',)

    ordering = ('phone_number',)

    add_fieldsets = (
        ("User Details", {'fields': (
                'phone_number', 
                'password1', 
                'password2', 
                'first_name',
                'last_name',
                'telegram_user_id',
            )
        }),
    )

admin.site.register(models.CustomUser, CustomUserAdmin)
