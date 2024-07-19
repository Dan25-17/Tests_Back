from django.urls import path, include
from rest_framework import routers


from .views import QuestionViewset, StudentsViewset

router = routers.DefaultRouter()
router.register(r'api/questions', QuestionViewset)
router.register(r'api/students', StudentsViewset)

urlpatterns = [
    path('', include(router.urls))
] 


