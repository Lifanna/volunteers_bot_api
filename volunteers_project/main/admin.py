from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from . import models
import csv
from django.http import HttpResponse
from django.db.models import Count, F
from django.db.models import Case, IntegerField, Sum, When


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

def export_to_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="volunteers.csv"'

    # Открываем файл CSV для записи с явным указанием кодировки
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow(['Район', 'Волонтер', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'])

    # # Получаем список уникальных месяцев
    # unique_months = models.UserWork.objects.filter(status='подтверждено').dates('created_at', 'month').distinct()

    # # Создаем динамические аннотации для каждого месяца
    # month_annotations = {}
    # for month in unique_months:
    #     month_name = month.strftime('%B')  # Название месяца на русском
    #     annotation_name = f'link_count_{month_name}'
    #     month_annotation = Sum(Case(When(created_at__month=month.month, then=1), default=0, output_field=IntegerField()))
    #     month_annotations[annotation_name] = month_annotation

    from django.db.models import Sum, Case, When, IntegerField

    # Получаем список уникальных месяцев
    unique_months = models.UserWork.objects.filter(status='подтверждено').dates('created_at', 'month').distinct()

    # Создаем динамические аннотации для каждого месяца
    month_annotations = {}
    for month in unique_months:
        month_name = month.strftime('%B')  # Название месяца на русском
        annotation_name = f'link_count_{month_name}'
        month_annotation = Sum(Case(When(created_at__month=month.month, then=1), default=0, output_field=IntegerField()))
        month_annotations[annotation_name] = month_annotation

    # Получаем данные с суммированием по месяцам и группировкой по пользователям
    user_data = models.UserWork.objects.filter(status='подтверждено').values(
        'user__region__name', 'user__phone_number'
    ).annotate(**month_annotations).order_by('user__region__name', 'user__phone_number')

    # Формируем CSV-файл
    for user_work in user_data:
        row = [
            user_work['user__region__name'],
            user_work['user__phone_number'],
        ]
        for month_name in month_annotations.keys():
            row.append(user_work[month_name])
        writer.writerow(row)

    # # Формируем запрос с динамическими аннотациями
    # link_count_by_month = models.UserWork.objects.filter(status='подтверждено').annotate(
    #     **month_annotations
    # ).values(
    #     'user__region__name', 'user__phone_number', *month_annotations.keys()
    # ).order_by('user__region__name', 'user__phone_number')

    # print("LINKSSSS:", link_count_by_month)

    # # for user_work in link_count_by_month:
    # #     writer.writerow([user_work.user.username, user_work.user.email, user_work.other_field])
    # for user_work in link_count_by_month:
    #     row = [
    #         user_work['user__region__name'],
    #         user_work['user__phone_number'],
    #     ]
    #     # Добавляем значения для каждого месяца в строку
    #     for month_name in month_annotations.keys():
    #         row.append(user_work[month_name])
    #     writer.writerow(row)

    return response


class UserWorkAdmin(admin.ModelAdmin):
    actions = [
        export_to_excel
    ]

admin.site.register(models.UserWork, UserWorkAdmin)

admin.site.register(models.Region)

admin.site.register(models.UserScore)

admin.site.register(models.Task)

admin.site.register(models.UserTask)
