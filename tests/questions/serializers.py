from rest_framework import serializers

from .models import Question, StudentAnswers, StudentList


class Question_Serializer(serializers.ModelSerializer):
    name = serializers.PrimaryKeyRelatedField(
    read_only=True
    )
    task = serializers.PrimaryKeyRelatedField(
    read_only=True
    )
    class Meta:
        model = Question
        fields = ('name', 'task', 'order')


class AnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswers
        fields = ('question', 'user', 'first_answer', 'correct_or_not', 'last_answer')


class StudentListSerializer(serializers.ModelSerializer):
    first_name = serializers.PrimaryKeyRelatedField(
    read_only=True
    )
    last_name = serializers.PrimaryKeyRelatedField(
    read_only=True
    )
    tg_id = serializers.PrimaryKeyRelatedField(
    read_only=True
    )

    class Meta:
        model  = StudentList
        fields = ('first_name', 'last_name', 'tg_id')