# quizapp/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterView, home_view, teacher_dashboard 

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
]