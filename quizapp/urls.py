# quizapp/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterView, home_view, teacher_dashboard, ExamCreateView, ExamUpdateView, ExamDeleteView, exam_detail_teacher, question_create_update, QuestionDeleteView, StudentExamListView, student_exam_take, student_exam_result

urlpatterns = [
    path('', home_view, name='home'),
    
    # URL cho Đăng ký
    path('register/', RegisterView.as_view(), name='register'),
    
    # URL cho Đăng nhập (sử dụng LoginView có sẵn)
    path('login/', LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True # Tự động chuyển hướng nếu người dùng đã đăng nhập
    ), name='login'),
    
    # URL cho Đăng xuất (sử dụng LogoutView có sẵn)
    path('logout/', LogoutView.as_view(), name='logout'),

    path('dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/exam/create/', ExamCreateView.as_view(), name='exam_create'),
    path('dashboard/exam/<int:pk>/update/', ExamUpdateView.as_view(), name='exam_update'),
    path('dashboard/exam/<int:pk>/delete/', ExamDeleteView.as_view(), name='exam_delete'),
    
    path('dashboard/exam/<int:pk>/', exam_detail_teacher, name='exam_detail_teacher'),
    path('dashboard/exam/<int:exam_pk>/question/create/', question_create_update, name='question_create'),
    path('dashboard/exam/<int:exam_pk>/question/<int:question_pk>/update/', question_create_update, name='question_update'),
    path('dashboard/exam/<int:exam_pk>/question/<int:pk>/delete/', QuestionDeleteView.as_view(), name='question_delete'),

    path('exams/', StudentExamListView.as_view(), name='student_exam_list'),
    path('exam/<int:pk>/take/', student_exam_take, name='student_exam_take'),
    path('result/<int:pk>/', student_exam_result, name='student_exam_result'),
]