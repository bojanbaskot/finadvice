from django.urls import path
from . import views

app_name = 'elearning'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course-list'),
    path('kurs/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('kurs/<slug:cslug>/lekcija/<slug:slug>/', views.LessonDetailView.as_view(), name='lesson-detail'),
    path('kviz/<int:pk>/', views.QuizView.as_view(), name='quiz'),
    path('kviz/<int:pk>/submit/', views.QuizSubmitView.as_view(), name='quiz-submit'),
    path('kviz/rezultat/<int:pk>/', views.QuizResultView.as_view(), name='quiz-result'),
]
