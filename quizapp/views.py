# quizapp/views.py

# --- Django Imports ---
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.http import HttpResponseForbidden

# --- Authentication Imports ---
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

# --- Local Imports ---
from .models import Exam, Question, Result
from .forms import CustomUserCreationForm, ExamForm, QuestionForm, ChoiceFormSet, MatchPairFormSet
import random

# =======================================================
# VIEWS XÁC THỰC VÀ TRANG CHỦ
# =======================================================

class RegisterView(CreateView):
    """View để đăng ký người dùng mới."""
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        login(self.request, user)
        return response

def home_view(request):
    """View cho trang chủ."""
    return render(request, 'home.html')

# =======================================================
# MIXINS VÀ HÀM KIỂM TRA QUYỀN
# =======================================================

def is_teacher(user):
    """Hàm trợ giúp để kiểm tra vai trò giáo viên."""
    return user.is_authenticated and user.role == 'TEACHER'

class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin đảm bảo người dùng là giáo viên đã đăng nhập."""
    def test_func(self):
        return is_teacher(self.request.user)

class ExamOwnerRequiredMixin(TeacherRequiredMixin):
    """Mixin đảm bảo người dùng là chủ sở hữu của bài thi."""
    def test_func(self):
        exam = self.get_object() 
        return super().test_func() and exam.owner == self.request.user

class QuestionOwnerRequiredMixin(TeacherRequiredMixin):
    """Mixin đảm bảo người dùng là chủ sở hữu của câu hỏi (thông qua bài thi)."""
    def test_func(self):
        question = self.get_object()
        return super().test_func() and question.exam.owner == self.request.user

# =======================================================
# VIEWS CHO GIÁO VIÊN (DASHBOARD & QUẢN LÝ EXAM)
# =======================================================

@login_required(login_url='login')
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    """Hiển thị bảng điều khiển cho giáo viên."""
    exams = Exam.objects.filter(owner=request.user).order_by('-created_at')
    context = {'exams': exams}
    return render(request, 'dashboard/teacher_dashboard.html', context)

class ExamCreateView(TeacherRequiredMixin, CreateView):
    """View để tạo bài thi mới."""
    model = Exam
    form_class = ExamForm
    template_name = 'dashboard/exam_form.html'
    success_url = reverse_lazy('teacher_dashboard')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Tạo bài thi mới'
        return context

class ExamUpdateView(ExamOwnerRequiredMixin, UpdateView):
    """View để cập nhật bài thi."""
    model = Exam
    form_class = ExamForm
    template_name = 'dashboard/exam_form.html'
    success_url = reverse_lazy('teacher_dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Chỉnh sửa: {self.object.title}'
        return context

class ExamDeleteView(ExamOwnerRequiredMixin, DeleteView):
    """View để xóa bài thi."""
    model = Exam
    template_name = 'dashboard/exam_confirm_delete.html'
    success_url = reverse_lazy('teacher_dashboard')

# =======================================================
# VIEWS QUẢN LÝ CÂU HỎI (QUESTION)
# =======================================================

@login_required
@user_passes_test(is_teacher)
def exam_detail_teacher(request, pk):
    """Hiển thị chi tiết một bài thi để quản lý câu hỏi."""
    exam = get_object_or_404(Exam, pk=pk)
    if exam.owner != request.user:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")
    
    questions = exam.questions.all().order_by('order')
    context = {'exam': exam, 'questions': questions}
    return render(request, 'dashboard/exam_detail_teacher.html', context)

@login_required
@user_passes_test(is_teacher)
@transaction.atomic # Đảm bảo tất cả các thao tác CSDL thành công hoặc không gì cả
def question_create_update(request, exam_pk, question_pk=None):
    """
    View để tạo hoặc cập nhật một câu hỏi.
    Đã được nâng cấp để xử lý nhiều loại formset một cách linh hoạt.
    """
    exam = get_object_or_404(Exam, pk=exam_pk)
    if exam.owner != request.user:
        return HttpResponseForbidden("Bạn không có quyền truy cập.")

    if question_pk:
        question = get_object_or_404(Question, pk=question_pk)
        page_title = "Chỉnh sửa câu hỏi"
    else:
        question = Question(exam=exam)
        page_title = "Tạo câu hỏi mới"

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        
        # Khởi tạo cả hai loại formset với dữ liệu POST
        # Thêm prefix để tránh xung đột tên trường giữa các formset
        choice_formset = ChoiceFormSet(request.POST, instance=question, prefix='choices')
        match_formset = MatchPairFormSet(request.POST, instance=question, prefix='matches')

        # Xác định formset nào cần được xác thực dựa trên loại câu hỏi được gửi lên
        q_type = form.data.get('question_type')
        formset_to_validate = None
        if q_type in [Question.QuestionType.SINGLE, Question.QuestionType.MULTIPLE, Question.QuestionType.TRUE_FALSE, Question.QuestionType.FILL_IN_BLANK]:
            formset_to_validate = choice_formset
        elif q_type == Question.QuestionType.MATCHING:
            formset_to_validate = match_formset

        if form.is_valid() and (formset_to_validate is None or formset_to_validate.is_valid()):
            saved_question = form.save()
            if formset_to_validate:
                formset_to_validate.instance = saved_question
                formset_to_validate.save()
            return redirect('exam_detail_teacher', pk=exam.pk)
        # Nếu không hợp lệ, request sẽ đi xuống và render lại trang với lỗi
            
    else: # GET request
        form = QuestionForm(instance=question)
        choice_formset = ChoiceFormSet(instance=question, prefix='choices')
        match_formset = MatchPairFormSet(instance=question, prefix='matches')

    context = {
        'form': form,
        'choice_formset': choice_formset,
        'match_formset': match_formset,
        'exam': exam,
        'page_title': page_title,
    }
    return render(request, 'dashboard/question_form.html', context)

class QuestionDeleteView(QuestionOwnerRequiredMixin, DeleteView):
    """View để xóa một câu hỏi."""
    model = Question
    template_name = 'dashboard/question_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('exam_detail_teacher', kwargs={'pk': self.object.exam.pk})

# =======================================================
# VIEWS CHO HỌC SINH
# =======================================================

class StudentExamListView(LoginRequiredMixin, ListView):
    """
    View này hiển thị danh sách tất cả các bài thi có sẵn cho học sinh.
    """
    model = Exam
    template_name = 'student/exam_list.html'  # Template mới cho học sinh
    context_object_name = 'exams' # Tên biến sẽ dùng trong template
    ordering = ['-created_at'] # Sắp xếp bài thi mới nhất lên đầu
    login_url = 'login' # Chuyển hướng đến trang đăng nhập nếu chưa login


@login_required(login_url='login')
def student_exam_take(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    # Lấy câu hỏi và các đối tượng liên quan để tối ưu truy vấn
    questions = exam.questions.prefetch_related('choices', 'match_pairs').all().order_by('order')

    if request.method == 'POST':
        score = 0
        total_questions = len(questions)

        for question in questions:
            q_id = str(question.id)
            
            if question.question_type == 'SINGLE':
                selected_choice_id = request.POST.get(f'question{q_id}')
                if selected_choice_id and question.choices.filter(id=selected_choice_id, is_correct=True).exists():
                    score += 1

            elif question.question_type == 'MULTIPLE':
                selected_ids = request.POST.getlist(f'question{q_id}')
                correct_ids = set(str(c.id) for c in question.choices.filter(is_correct=True))
                if set(selected_ids) == correct_ids:
                    score += 1
            
            elif question.question_type == 'TRUE_FALSE':
                # Logic chấm cho dạng Đúng/Sai mới
                all_sub_questions_correct = True
                for choice in question.choices.all():
                    user_answer = request.POST.get(f'question{q_id}_choice{choice.id}') # "Đúng" hoặc "Sai"
                    correct_answer = "Đúng" if choice.is_correct else "Sai"
                    if user_answer != correct_answer:
                        all_sub_questions_correct = False
                        break
                if all_sub_questions_correct:
                    score += 1

            elif question.question_type == 'FILL_IN_BLANK':
                user_answer = request.POST.get(f'question{q_id}', '').strip()
                correct_choice = question.choices.first()
                if correct_choice and user_answer.lower() == correct_choice.text.strip().lower():
                    score += 1

            elif question.question_type == 'MATCHING':
                # Logic chấm cho dạng Ghép đôi
                all_pairs_correct = True
                for pair in question.match_pairs.all():
                    user_answer_for_prompt = request.POST.get(f'question{q_id}_prompt{pair.id}')
                    if user_answer_for_prompt != pair.answer:
                        all_pairs_correct = False
                        break
                if all_pairs_correct:
                    score += 1

        # Lưu kết quả
        result = Result.objects.create(
            student=request.user,
            exam=exam,
            score=score,
            total=total_questions
        )
        # Chuyển hướng đến trang kết quả
        return redirect('student_exam_result', pk=result.pk)

    # Chuẩn bị dữ liệu cho câu hỏi ghép đôi (xáo trộn các câu trả lời)
    for q in questions:
        if q.question_type == 'MATCHING':
            answers = list(p.answer for p in q.match_pairs.all())
            random.shuffle(answers)
            q.shuffled_answers = answers

    context = {
        'exam': exam,
        'questions': questions
    }
    return render(request, 'student/exam_take.html', context)

@login_required(login_url='login')
def student_exam_result(request, pk):
    result = get_object_or_404(Result, pk=pk, student=request.user)
    context = {
        'result': result
    }
    return render(request, 'student/exam_result.html', context)
