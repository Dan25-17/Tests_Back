from django.db import models

from django.contrib.auth.models import AbstractUser

MAX_CHARFIELD_LENGTH = 500
MAX_TEXTFIELD_LENGTH = 1000
MAX_USER_CHARFIELD_LENGTH = 150




# 1 - 1000 - 1999
# 2 - 2000 - 2999
# 27 - 27000 - 27999
# def set_order(question):
#     q = Question.objects.filter(task_number=question.task_number).order_by('ordering').last()
#     return question.task_number * 1000 + (q.ordering - question.task_number * 1000) + 1



# модель настройки количества вопросов для отправки
class QuestionSettings(models.Model):
    questions_per_page = models.IntegerField(
        verbose_name='Количество вопросов',
        help_text='Сколько вопросов ученик получит за один раз'
        )

    class Meta:
        verbose_name = 'Настройки количества вопросов'
        verbose_name_plural = 'Настройки количества вопросов'

    def __str__(self) -> str:
        return str(self.questions_per_page)



# модель списка заданий в егэ
class TaskNumber(models.Model):
    number = models.IntegerField(verbose_name='Номер задания в ЕГЭ')

    class Meta:
        verbose_name = 'номер задания в егэ'
        verbose_name_plural = 'Номера задания в егэ'

    def __str__(self) -> str:
        return str(self.number)


# модель вопросов
class Question(models.Model):
    class QuestionTypeChoises(models.TextChoices):  # только для бота и оформления вопроса в боте
        TYPE1 = '1', 'Один ответ'
        TYPE2 = '2', 'Множественный ответ'
        TYPE3 = '3', 'Открытый ответ'
        TYPE4 = '4', 'Сопоставление'
    # что в коде = что в бд, что мы видим в админке

    order = models.IntegerField(
        verbose_name='Порядковый номер вопроса',
        unique=True
    )
    name = models.CharField(
        verbose_name='Текст вопроса',
        max_length=MAX_CHARFIELD_LENGTH,
        help_text='Задание - что ученику нужно сделать'
    )
    task = models.TextField(
        verbose_name='Текст задания',
        max_length=MAX_TEXTFIELD_LENGTH,
        help_text='Текст задания, в котором ученику нужно что-то сделать',
        blank=True, null=True
    )
    task_number = models.ForeignKey(
        TaskNumber,
        related_name='questions',
        verbose_name='Номер задания в ЕГЭ',
        on_delete=models.CASCADE
    )
    answers = models.CharField(
        verbose_name='Варианты ответов',
        max_length=MAX_CHARFIELD_LENGTH,
        blank=True, null=True
    )
    correct = models.JSONField(
        verbose_name='Правильный ответ',
        help_text='Вставить в квадратные скобки в кавычках, через запятую, например: "1", "2", "3" ',
        default=dict((('answers', list()),))
    )
    #  {'type': 'any', 'answer': ['one', 'two']} необходим хотя бы один из списка
    #  {'type': 'all', 'answer': [1, 4, 7, 3]} необходимы все варианты из списка
    answer_type = models.CharField(
        verbose_name='Тип ответа',
        choices=(('any', 'Допустим один из вариантов'), ('all', 'Один вариант')),
        max_length=MAX_CHARFIELD_LENGTH
    )
    explanation = models.TextField(
        verbose_name='Текстовое объяснение ошибки',
        max_length=MAX_TEXTFIELD_LENGTH,
    )
    file = models.FileField(
        verbose_name='Файл с объяснением',
        upload_to='uploads/%Y/%m/%d/',
        blank=True,
        null=True
    )
    type_of_question = models.CharField(
        verbose_name='Тип вопроса',
        choices=QuestionTypeChoises.choices,
        max_length=MAX_CHARFIELD_LENGTH
    )

    is_dubble = models.BooleanField(default=False) # является ли дублем
    dubbled_question = models.ForeignKey('Question', 
        related_name='dubble',
        verbose_name='Чей дублер',
        on_delete=models.CASCADE,
        blank=True, null=True
        ) 
    # кого дублирует

    class Meta:
        verbose_name = 'вопросы'
        verbose_name_plural = 'Вопросы'
        ordering = ('order', )
        # валидация того, что оба task и answers не могут быть пустыми

    def __str__(self):
        return f'{self.order}. {self.name}'


# модель списка учеников
class StudentList(models.Model):
    first_name = models.CharField(
        verbose_name='Имя ученика',
        max_length=MAX_USER_CHARFIELD_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='Фамилия ученика',
        max_length=MAX_USER_CHARFIELD_LENGTH,
    )
    tg_id = models.CharField(
        verbose_name='ID в Телеграм',
        max_length=MAX_USER_CHARFIELD_LENGTH,
    )
    
    class Meta:
        verbose_name = 'список учеников'
        verbose_name_plural = 'Списки учеников' 


    def __str__(self) -> str:
        return self.last_name


# модель ответов учеников
class StudentAnswers(models.Model):
    question = models.ForeignKey(
        Question,
        verbose_name='Вопрос',
        related_name='students_answers',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        StudentList,
        verbose_name='Ученик',
        related_name='answers',
        on_delete=models.CASCADE
    )
    first_answer = models.CharField(
        verbose_name='Первый ответ ученика',
        max_length=MAX_CHARFIELD_LENGTH,
    )
    correct_or_not = models.BooleanField(
        verbose_name='Правильность ответа'
    )
    last_answer = models.CharField(
        verbose_name='Последний ответ ученика',
        max_length=MAX_CHARFIELD_LENGTH,
    )
    dubble_sent = models.BooleanField(
        verbose_name='Отправлен ли дубль',
        default=True
    )

    class Meta:
        verbose_name = 'ответы учеников'
        verbose_name_plural = 'Ответы учеников'


    def __str__(self):
        return self.user.last_name


    # @property # свойство/вычисляемое свойство    answer.is_correct
    # def correct_or_not(self):
    #     if self.question.answer == self.last_answer:
    #         return True
    #     return False


# модель пользователя
class CustomUser(AbstractUser):
    username = models.CharField(
        verbose_name='Username',
        max_length=MAX_USER_CHARFIELD_LENGTH,
        unique=True
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=MAX_USER_CHARFIELD_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_USER_CHARFIELD_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_USER_CHARFIELD_LENGTH,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_USER_CHARFIELD_LENGTH,
    )
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email', 'password', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи' 
