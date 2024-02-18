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


class Region(models.Model):
    name = models.CharField("Наименование региона", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=50, unique=True)

    first_name = models.CharField(max_length=12, verbose_name='Имя', null=True)
    
    last_name = models.CharField(max_length=12, verbose_name='Фамилия', null=True)
    
    is_active = models.BooleanField(default=True, verbose_name='Прошел активацию')
    
    is_staff = models.BooleanField(default=False, verbose_name='Служебный аккаунт')

    DIRECTION_CHOICES = (
        ('нарко', 'нарко'),
        ('экологическое', 'экологическое'),
        ('культурное', 'культурное'),
        ('спортивное', 'спортивное'),
    )

    region = models.ForeignKey(Region, verbose_name="Район", on_delete=models.CASCADE, null=True)

    direction = models.CharField("Направление", max_length=20, choices=DIRECTION_CHOICES)

    telegram_user_id = models.CharField("Телеграм ID", max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

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


class UserWork(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name="Пользователь", on_delete=models.CASCADE)

    link = models.URLField("Ссылка")

    STATUS_CHOICES = (
        ('подтверждено', 'Подтверждено'),
        ('не подтверждено', 'Не подтверждено'),
        ('новое', 'Новое'),
    )

    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.telegram_user_id

    class Meta:
        verbose_name = 'Работа пользователя'
        verbose_name_plural = 'Работы пользователей'


class UserScore(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name="Пользователь", on_delete=models.CASCADE)

    score = models.PositiveIntegerField("Балл")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user

    class Meta:
        verbose_name = 'Балл пользователя'
        verbose_name_plural = 'Баллы пользователей'


class Task(models.Model):
    name = models.CharField("Наименование задания", max_length=255)

    text = models.TextField("Брифинг задания")

    score = models.IntegerField("Количество баллов за задание")

    start_date = models.DateField("Период: начало")

    end_date = models.DateField("Период: завершение")

    assigned = models.BooleanField("Назначено", default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'


class UserTask(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name="Волонтер")

    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, verbose_name="Задание")

    STATUS_CHOICES = (
        ('выполнено', 'Выполнено'),
        ('на выполнении', 'На выполнении'),
        ('не выполнено', 'Не выполнено'),
    )

    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='на выполнении')

    def __str__(self):
        return self.user.telegram_user_id + " / " + self.task.name

    class Meta:
        verbose_name = 'Назначенное задание'
        verbose_name_plural = 'Назначенные задания'
