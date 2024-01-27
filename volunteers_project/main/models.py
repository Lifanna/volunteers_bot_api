from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number or password is None:
            raise ValueError('Phone number is required field.')

        # phone_number = self.normalize_email(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        if not phone_number or password is None:
            raise ValueError('Required.')

        extra_fields['is_superuser'] = True
        extra_fields['is_staff'] = True

        # phone_number = self.normalize_email(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)

        user.set_password(password)
        user.save()

        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=50, unique=True)

    first_name = models.CharField(max_length=12, verbose_name='Имя', null=True)
    
    last_name = models.CharField(max_length=12, verbose_name='Фамилия', null=True)
    
    is_active = models.BooleanField(default=True, verbose_name='Прошел активацию')
    
    is_staff = models.BooleanField(default=False, verbose_name='Служебный аккаунт')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    telegram_user_id = models.CharField("Телеграм ID", max_length=255, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def has_perm(*args, **kwargs):
        return True

    def has_module_perms(*args, **kwargs):
        return True

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
