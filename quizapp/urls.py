from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Auth & Home
    path('', views.home_view, name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='registration/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Teacher Dashboard & Exam CRUD
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/exam/create/', views.ExamCreateView.as_view(), name='exam_create'),
    path('dashboard/exam/<int:pk>/update/', views.ExamUpdateView.as_view(), name='exam_update'),
    path('dashboard/exam/<int:pk>/delete/', views.ExamDeleteView.as_view(), name='exam_delete'),
    path('dashboard/passage/<int:pk>/update/', views.ReadingPassageUpdateView.as_view(), name='passage_update'),
    
    # Teacher Question Management
    path('dashboard/exam/<int:pk>/', views.exam_detail_teacher, name='exam_detail_teacher'),
    path('dashboard/exam/<int:exam_pk>/question/create/', views.question_create_update, name='question_create'),
    path('dashboard/exam/<int:exam_pk>/question/<int:question_pk>/update/', views.question_create_update, name='question_update'),
    path('dashboard/exam/question/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
    path('dashboard/exam/<int:pk>/history/', views.ExamResultHistoryView.as_view(), name='exam_result_history'),
    path('dashboard/result/<int:pk>/view/', views.teacher_result_detail, name='teacher_result_detail'),

    # Student Exam Flow
    path('exams/', views.StudentExamListView.as_view(), name='student_exam_list'),
    path('join-exam/', views.join_exam_by_code, name='join_exam_by_code'),
    path('exam/<int:pk>/start/', views.start_exam, name='start_exam'),
    path('exam/<int:pk>/take/', views.student_exam_take, name='student_exam_take'),
    path('exam/<int:pk>/take/section/<int:section_order>/', views.student_exam_take_sectional, name='student_exam_take_section'),
    path('result/<int:pk>/', views.student_exam_result, name='student_exam_result'),
    # BỔ SUNG URL CHO TRANG LỊCH SỬ
    path('history/', views.StudentResultHistoryView.as_view(), name='student_result_history'),

    path('account/', views.AccountInfoUpdateView.as_view(), name='account_info'),
]
