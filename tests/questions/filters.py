from django_filters import rest_framework as filters
from django.db.models import F

from .models import Question, StudentAnswers


class QuestionFilter(filters.FilterSet):
    page = filters.NumberFilter(method='get_page')
    task = filters.NumberFilter(method='get_task')
    user = filters.NumberFilter(method='get_user')
    # dubbles = filters.NumberFilter(method='get_dubbles')
    answered = filters.NumberFilter(method='get_answered')

    class Meta:
        model = Question
        fields = ('page', )

    def get_page(self, queryset, name, value):
        if value:
            return queryset[(value - 1)*20:value*20]
        return queryset
    
    def get_task(self, queryset, name, value):
        if value:
            return queryset.filter(task_number__number=value)
        return queryset
    
    def get_user(self, queryset, name, value):
        if value:
            return queryset.filter(students_answers__user__tg_id=value).filter(students_answers__correct_or_not=False)
        return queryset
    
    def get_correct(self, queryset, name, value):
        if value:
            if value == 1:
                return queryset.filter(students_answers__first_answer=F('students_answers__last_answer'))
            elif value == 0:
                return queryset.exclude(students_answers__first_answer=F('students_answers__last_answer'))
        return queryset
