# quizapp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Exam, Question
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test

# --- View cho Đăng ký ---
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html' # Template chúng ta sẽ tạo ở bước sau
    success_url = reverse_lazy('home') # Chuyển hướng đến trang chủ sau khi đăng ký thành công

    def form_valid(self, form):
        # Tự động đăng nhập cho người dùng sau khi đăng ký thành công
        response = super().form_valid(form)
        user = self.object
        login(self.request, user)
        return response

# --- Các view khác (để test redirect) ---
def home_view(request):
    return render(request, 'home.html')

def exam_list(request):
    """
    Hiển thị danh sách tất cả các kỳ thi.
    """
    exams = Exam.objects.all()
    return render(request, 'quizapp/exam_list.html', {'exams': exams})

def exam_detail(request, exam_id):
    """
    Hiển thị chi tiết một kỳ thi, bao gồm các câu hỏi và lựa chọn.
    """
    exam = get_object_or_404(Exam, pk=exam_id)
    return render(request, 'quizapp/exam_detail.html', {'exam': exam})

def submit_exam(request, exam_id):
    """
    Xử lý việc nộp bài và tính điểm.
    """
    if request.method == 'POST':
        exam = get_object_or_404(Exam, pk=exam_id)
        score = 0
        total_questions = 0
        for question in exam.question_set.all():
            total_questions += 1
            selected_choice_id = request.POST.get(f'question{question.id}')
            if selected_choice_id:
                correct_choice = question.choice_set.get(is_correct=True)
                if int(selected_choice_id) == correct_choice.id:
                    score += 1
        
        # Lưu kết quả vào session hoặc database (ở đây chỉ render)
        context = {
            'score': score,
            'total': total_questions,
            'exam': exam
        }
        return render(request, 'quizapp/exam_result.html', context)
    
    # Nếu không phải POST, chuyển hướng về trang chi tiết
    return redirect('exam_detail', exam_id=exam_id)

# --- Hàm kiểm tra vai trò ---
def is_teacher(user):
    """Hàm này kiểm tra xem người dùng có phải là giáo viên không."""
    return user.is_authenticated and user.role == 'TEACHER'

# --- View cho Dashboard của Giáo viên ---
@login_required(login_url='login') # 1. Yêu cầu người dùng phải đăng nhập
@user_passes_test(is_teacher)      # 2. Kiểm tra xem người dùng có phải là giáo viên không
def teacher_dashboard(request):
    """
    Hiển thị trang tổng quan cho giáo viên, bao gồm danh sách các kỳ thi
    mà họ đã tạo.
    """
    # Lấy tất cả các kỳ thi do chính giáo viên này tạo ra
    exams = Exam.objects.filter(owner=request.user).order_by('-created_at')
    
    context = {
        'exams': exams
    }
    return render(request, 'dashboard/teacher_dashboard.html', context)