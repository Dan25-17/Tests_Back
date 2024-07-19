from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Question, StudentAnswers, TaskNumber, StudentList, CustomUser, QuestionSettings
from .forms import MyUserChangeForm


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = MyUserChangeForm
    # list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    # list_filter = ('first_name', 'email')


@admin.register(QuestionSettings)
class QuestionAdmin(admin.ModelAdmin):
    # fields = ('__all__', )
    # list_display = '__all__'
    list_filter = ('questions_per_page',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    # fields = ('__all__', )
    # list_display = '__all__'
    list_filter = ('task_number',)


@admin.register(TaskNumber)
class TaskAdmin(admin.ModelAdmin):
    # fields = ('__all__', )
    pass
    # list_display = '__all__'


@admin.register(StudentList)
class StudentAdmin(admin.ModelAdmin):
    # fields = ('__all__', )
    pass
    # list_display = '__all__'


@admin.register(StudentAnswers)
class AnswersAdmin(admin.ModelAdmin):
    # fields = ('__all__', )
    list_filter = ('question__task_number', 'user')
    # list_display = '__all__'

