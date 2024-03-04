from rest_framework import serializers
from . import models


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = "__all__"


class UserWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserWork
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = "__all__"


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = '__all__'


class UserScoreSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    class Meta:
        model = models.UserScore
        fields = "__all__"


class UserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserTask
        fields = '__all__'
