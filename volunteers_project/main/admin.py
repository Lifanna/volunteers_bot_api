from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from . import models


class CustomUserAdmin(UserAdmin):
    """Регистрация модели CustomUser в админ панели"""
    fieldsets = (
        (None, {'fields': ('password',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number','telegram_user_id', 'direction', 'region',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions',),
        }),
        ('Important dates', {'fields': ('last_login',)}),
    )

    list_display = ('__str__', 'phone_number', 'telegram_user_id', 'direction', 'region',)

    list_filter = ('phone_number', 'first_name', 'last_name', 'direction', 'region',)

    search_fields = ('phone_number', 'first_name', 'last_name', 'direction', 'region',)

    ordering = ('phone_number', 'direction', 'region',)

    add_fieldsets = (
        ("User Details", {'fields': (
                'phone_number', 
                'password1', 
                'password2', 
                'first_name',
                'last_name',
                'telegram_user_id',
                'direction',
                'region',
            )
        }),
    )

admin.site.register(models.CustomUser, CustomUserAdmin)

admin.site.register(models.UserWork)

admin.site.register(models.Region)

admin.site.register(models.UserScore)

admin.site.register(models.Task)

admin.site.register(models.UserTask)
