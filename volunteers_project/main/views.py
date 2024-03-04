from django.shortcuts import render
from rest_framework import views, generics
from rest_framework import status
from rest_framework.response import Response
from . import models, serializers
from django.db.models import Q
from django.utils import timezone


def index(request):
    return render(request, 'main/index.html')


class LoginAPIView(views.APIView):
    def post(self, request):
        telegram_user_id = request.data.get('telegram_user_id')
        user = models.CustomUser.objects.filter(telegram_user_id=telegram_user_id)

        try:
            user = models.CustomUser.objects.get(telegram_user_id=telegram_user_id)
        except models.CustomUser.DoesNotExist:
            return Response({"detail": "Пользователь с таким номером телефона не найден"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Пользователь успешно аутентифицирован и обновлен"}, status=status.HTTP_200_OK)


class VerifyAPIView(views.APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        telegram_user_id = request.data.get('telegram_user_id')

        try:
            user = models.CustomUser.objects.get(phone_number=phone_number)
        except models.CustomUser.DoesNotExist:
            return Response({"detail": "Пользователь с таким номером телефона не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Обновление telegram_user_id
        user.telegram_user_id = telegram_user_id
        user.save()

        return Response({"detail": "Пользователь успешно аутентифицирован и обновлен"}, status=status.HTTP_200_OK)


class UserWorkCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.UserWorkSerializer

    def create(self, request, *args, **kwargs):
        telegram_user_id = request.data.get('telegram_user_id')
        link = request.data.get('link')

        try:
            user = models.CustomUser.objects.get(telegram_user_id=telegram_user_id)
        except models.CustomUser.DoesNotExist:
            return Response({"detail": "Пользователь с таким telegram_user_id не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Создаем запись о работе пользователя
        user_work = models.UserWork.objects.create(user=user, link=link, status='не подтверждено')
        # user_score, created = models.UserScore.objects.get_or_create(user=user)
        
        if models.UserScore.objects.filter(user=user).exists():
            user_score = models.UserScore.objects.get(user=user)
            user_score.score += 10
            user_score.save()
        else:
            models.UserScore.objects.create(user=user, score=10)

        serializer = self.get_serializer(user_work)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserProfileAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.UserProfileSerializer

    def get_object(self):
        telegram_user_id = self.kwargs.get('telegram_user_id')
        try:
            user = models.CustomUser.objects.get(telegram_user_id=telegram_user_id)
            return user
        except models.CustomUser.DoesNotExist:
            return None

    def get_queryset(self):
        return models.CustomUser.objects.filter(id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        # Информация о пользователе
        user_info = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "direction": user.direction,
        }

        # Количество ссылок за все время
        total_links = models.UserWork.objects.filter(user=user).count()

        # Подтвержденные за все время
        total_approved = models.UserWork.objects.filter(user=user, status='подтверждено').count()

        # Подтвержденные за текущий месяц до 25 числа
        current_month = timezone.now().month
        current_year = timezone.now().year
        total_approved_current_month = models.UserWork.objects.filter(
            Q(user=user),
            Q(status='подтверждено'),
            Q(created_at__month=current_month, created_at__year=current_year),
            Q(created_at__day__lte=25)
        ).count()

        user_info["total_links"] = total_links
        user_info["total_approved"] = total_approved
        user_info["total_approved_current_month"] = total_approved_current_month

        print("SSSS:", user_info)

        return Response(user_info)


class UserWorkListAPIView(generics.ListAPIView):
    serializer_class = serializers.UserWorkSerializer
    queryset = models.UserWork.objects.all()

    def get_queryset(self):
        telegram_user_id = self.kwargs.get("telegram_user_id")

        queryset = models.UserWork.objects.filter(
            user__telegram_user_id=telegram_user_id
        )

        return queryset


class TaskListAPIView(generics.ListAPIView):
    serializer_class = serializers.TaskSerializer
    queryset = models.Task.objects.all()

    def get_queryset(self):
        queryset = models.Task.objects.filter(
            assigned=False
        )[:10]

        return queryset


class RatingAPIView(generics.ListAPIView):
    model = models.UserScore
    queryset = models.UserScore.objects.all()
    serializer_class = serializers.UserScoreSerializer


class UserTaskCreateAPIView(generics.CreateAPIView):
    model = models.UserTask
    serializer_class = serializers.UserTaskSerializer
    queryset = models.UserTask.objects.all()

    def create(self, request, *args, **kwargs):
        # Получаем telegram_user_id из запроса
        telegram_user_id = request.data.get('user')

        print("USER: ", request.data)

        if telegram_user_id:
            user = models.CustomUser.objects.get(
                telegram_user_id=telegram_user_id,
            )

            task = models.Task.objects.get(
                pk=request.data.get('task'),
            )

            user_task = models.UserTask.objects.create(
                user=user,
                task=task,
                status='на выполнении'
            )

            update_task_by_pk(task.pk)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({}, status=status.HTTP_201_CREATED)

def update_task_by_pk(task_id):
    try:
        task = models.Task.objects.get(pk=task_id)
        task.assigned = True
        task.save()
        return task
    except models.Task.DoesNotExist:
        return None