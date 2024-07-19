from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import F

from .models import Question, StudentAnswers, StudentList, QuestionSettings
from .serializers import Question_Serializer, AnswersSerializer, StudentListSerializer



from django_filters.rest_framework import DjangoFilterBackend
from .filters import QuestionFilter

# Create your views here.


# вьюшка для вопросов
# get на получение всех
# get на получение одного

# Model 
# 1. Get 1
# 2. Get all
# 3. Add 1
# 4. Change 1 (Put/patch)
# 5. Delete 1

# ReadOnlyModel
# 1. Get 1
# 2. Get all



# @api_view(['GET'])
# def questions_list(request):
#     questions = Question.objects.all()
#     print(questions)
#     serializer = Question_Serializer(questions)
#     # permission_classes = [...]
#     return Response(serializer.data) 


# @api_view(['GET'])
# def questions_detail(request, pk):
#     question = get_object_or_404(Question, pk=pk)
#     serializer = Question_Serializer(question)
#     return Response(question.data) 


class QuestionViewset(viewsets.ReadOnlyModelViewSet):
    # /что-то/?page=353&num=356&text=46756 - get all
    # /что-то/pk/ - get 1
    serializer_class = Question_Serializer
    queryset = Question.objects.filter(is_dubble=False)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = QuestionFilter
    lookup_field = "order"
    # pagination class

    @action(methods=['GET'], detail=False)
    def free_for_student(self, request):
        task = request.GET.get('task')
        user = request.GET.get('user')
        student = StudentList.objects.get(tg_id=user)
        st_a = student.answers.filter(question__task_number__number=task)
        q1 = Question.objects.filter(students_answers__in=st_a) # уже ответил
        q2 = Question.objects.filter(is_dubble=False).filter(task_number__number=task).exclude(students_answers__in=st_a) # еще не ответил
        # q2 - список подходящих вопросов
        # q2 = q2[:20]
        number = int(str(QuestionSettings.objects.get(pk=1)))
        q2 = q2[:number]
        serializer = Question_Serializer(q2, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def dubbles(self, request):
        user = request.GET.get('user')
        task = request.GET.get('task')
        student = StudentList.objects.get(tg_id=user)
        # все неправильные ответы студента на определенный таск
        st_a = student.answers.filter(question__task_number__number=task).filter(dubble_sent=False)
        # соответствующие ответам вопросы
        queryset = Question.objects.filter(students_answers__in=st_a)
        # дубли этих вопросов
        qs = Question.objects.filter(is_dubble=True).filter(dubbled_question__in=queryset)
        serializer = Question_Serializer(qs, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def wrong(self, request):
        user = request.GET.get('user')
        task = request.GET.get('task')
        student = StudentList.objects.get(tg_id=user)

        # все неправильные ответы студента на определенный таск
        # print(student.answers)
        st_a = student.answers.filter(question__task_number__number=task).filter(correct_or_not=False)

        # соответствующие ответам вопросы
        queryset = Question.objects.filter(students_answers__in=st_a)
        serializer = Question_Serializer(queryset, many=True)
        return Response(serializer.data)
        
    

    @action(detail=True, methods=['POST'])
    # /что-то/student_answer/
    def student_answer(self, request, order):
        question = Question.objects.get(order=order) # 404
        data = request.data
        user = StudentList.objects.get(tg_id=data['user'])
        # допустим в теле запроса пришел json {'user': 111, 'answer': '2345'}
        # если человек на этот основной вопрос еще не отвечал
        if not StudentAnswers.objects.filter(user__tg_id=data['user'], question=question).exists():
            
            StudentAnswers.objects.create(
                user=user,
                question=question,
                first_answer=data['answer'],
                correct_or_not=False,
                last_answer=data['answer'])
            answer = StudentAnswers.objects.get(user=user, question=question)
            # то создали объект ответа
        else:
            # в противном случае нашли объект ответа
            answer = StudentAnswers.objects.get(user=user, question=question)
            if not question.is_dubble and not answer.correct_or_not:
                # то устанавливаем флажок "необходимо отправить дубль"
                answer.dubble_sent = False
            # если там уже все хорошо, то так и говорим
            if answer.correct_or_not:
                return Response({'answer': 'already correct'}, status=status.HTTP_200_OK)
        
        # если оказалось, что сейчас человек ответил на дубль
        if question.is_dubble:
            # то основному вопросу устанавливаем флажок "дубль был отправлен"
            q = question.dubbled_question
            dub_answer = StudentAnswers.objects.get(question=q)
            dub_answer.dubble_sent = True
            dub_answer.save()
        
        # проверяем правильность ответа
        answer.last_answer = data['answer']
        correct_answers = question.correct['answers']
        if question.answer_type == 'any':
            answer.correct_or_not = data['answer'] in correct_answers
        if question.answer_type == 'all':
            answer.correct_or_not = set(data['answer']) == set(map(str, correct_answers))
        answer.save()


        # высылаем респонс
        if answer.correct_or_not:
            return Response({'answer': 'correct'}, status=status.HTTP_200_OK)
        if not answer.correct_or_not:
            
            explanation = answer.question.explanation
            d = {'answer': 'wrong', 'explanation': explanation}
            # file = answer.question.file
            # if answer.question.file:
                # file = answer.question.file
                # d['file'] = file
            # расширить для проверки наличия файла с объяснением
            return Response(d, status=status.HTTP_200_OK)
        




# class AnswersViewSet(viewsets.ModelViewSet):
#     serializer_class = AnswersSerializer
#     queryset = StudentAnswers.objects.all()


@api_view(['POST'])
def student_answers(request):
    # answers = .objects.all()
    serializer = AnswersSerializer(data=request.data, many=True)
    return Response(serializer.data) 


class StudentsViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentListSerializer
    queryset = StudentList.objects.all()
    filter_backends = (DjangoFilterBackend, )

@api_view(['GET'])
def students_list(request):
    serializer = StudentListSerializer(data=request.data, many=True)
    return Response(serializer.data)