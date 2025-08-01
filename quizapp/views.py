from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.http import HttpResponseForbidden
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .models import Exam, Question, Result, ReadingPassage
from .forms import (
    CustomUserCreationForm, ExamForm, QuestionForm, ChoiceFormSet, 
    MatchPairFormSet, ExamSectionFormSet, ReadingPassageForm
)
import random

# --- VIEWS XÁC THỰC VÀ TRANG CHỦ ---
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """
        Ghi đè phương thức này để xử lý việc đăng nhập sau khi đăng ký.
        """
        # Lưu người dùng mới vào database
        user = form.save()
        
        # SỬA LỖI: Gán đối tượng người dùng vừa tạo cho self.object
        # trước khi gọi các hàm khác.
        self.object = user
        
        # Đăng nhập cho người dùng, chỉ định rõ backend sẽ sử dụng
        login(self.request, user, backend='quizapp.backends.EmailBackend')
        
        # Chuyển hướng đến trang thành công
        return redirect(self.get_success_url())

def home_view(request):
    return render(request, 'home.html')

# --- MIXINS VÀ HÀM KIỂM TRA QUYỀN ---
def is_teacher(user):
    return user.is_authenticated and user.role == 'TEACHER'

class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self): return is_teacher(self.request.user)

class ExamOwnerRequiredMixin(TeacherRequiredMixin):
    def test_func(self):
        exam = self.get_object() 
        return super().test_func() and exam.owner == self.request.user

class QuestionOwnerRequiredMixin(TeacherRequiredMixin):
    def test_func(self):
        question = self.get_object()
        return super().test_func() and question.exam.owner == self.request.user

# --- CÁC HẰNG SỐ CẤU HÌNH ---
EXAM_STRUCTURE = {
    'NATURAL_SCIENCES': {'Phần 1: Trắc nghiệm khách quan': {'type': Question.QuestionType.SINGLE, 'count': 18},'Phần 2: Trắc nghiệm Đúng/Sai': {'type': Question.QuestionType.TRUE_FALSE, 'count': 4},'Phần 3: Trả lời ngắn': {'type': Question.QuestionType.FILL_IN_BLANK, 'count': 6}},
    'MATH': {'Phần 1: Trắc nghiệm khách quan': {'type': Question.QuestionType.SINGLE, 'count': 12},'Phần 2: Trắc nghiệm Đúng/Sai': {'type': Question.QuestionType.TRUE_FALSE, 'count': 4},'Phần 3: Trả lời ngắn': {'type': Question.QuestionType.FILL_IN_BLANK, 'count': 6}},
    'SOCIAL_SCIENCES': {'Phần 1: Trắc nghiệm khách quan': {'type': Question.QuestionType.SINGLE, 'count': 24},'Phần 2: Trắc nghiệm Đúng/Sai': {'type': Question.QuestionType.TRUE_FALSE, 'count': 4}},
    'ENGLISH': {'Phần 1: Trắc nghiệm khách quan': {'type': Question.QuestionType.SINGLE, 'count': 40}},
    'TSA': {'Phần 1: Tư duy Toán học': {'type': Question.QuestionType.SINGLE, 'count': 40, 'duration': 60},'Phần 2: Tư duy Đọc hiểu - Ngữ liệu 1': {'type': Question.QuestionType.SINGLE, 'count': 10, 'duration': 30, 'passage_order': 1},'Phần 3: Tư duy Đọc hiểu - Ngữ liệu 2': {'type': Question.QuestionType.SINGLE, 'count': 10, 'duration': 30, 'passage_order': 2},'Phần 4: Tư duy Khoa học/Giải quyết vấn đề': {'type': Question.QuestionType.SINGLE, 'count': 40, 'duration': 60}}
}
SUBJECT_TO_STRUCTURE_KEY = {'MATH': 'MATH', 'PHYSICS': 'NATURAL_SCIENCES', 'CHEMISTRY': 'NATURAL_SCIENCES', 'BIOLOGY': 'NATURAL_SCIENCES', 'HISTORY': 'SOCIAL_SCIENCES', 'GEOGRAPHY': 'SOCIAL_SCIENCES', 'CIVIC_EDUCATION': 'SOCIAL_SCIENCES', 'ENGLISH': 'ENGLISH', 'TSA': 'TSA', 'OTHER': 'NATURAL_SCIENCES'}
EXAM_DURATION_MAP = {'MATH': 90, 'TSA': 150, 'DEFAULT': 50}

# --- VIEWS CHO GIÁO VIÊN ---
@login_required(login_url='login')
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    exams = Exam.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'dashboard/teacher_dashboard.html', {'exams': exams})

class ExamCreateView(TeacherRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'dashboard/exam_form_custom.html'
    success_url = reverse_lazy('teacher_dashboard')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['section_formset'] = ExamSectionFormSet(self.request.POST, prefix='sections')
        else:
            data['section_formset'] = ExamSectionFormSet(prefix='sections')
        data['page_title'] = 'Tạo bài thi mới'
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        section_formset = context['section_formset']
        with transaction.atomic():
            form.instance.owner = self.request.user
            is_custom = form.cleaned_data.get('is_custom')
            if not is_custom:
                subject = form.cleaned_data.get('subject')
                form.instance.duration_minutes = EXAM_DURATION_MAP.get(subject, EXAM_DURATION_MAP['DEFAULT'])
            self.object = form.save()
            if is_custom:
                if section_formset.is_valid():
                    section_formset.instance = self.object
                    section_formset.save()
                else:
                    return self.form_invalid(form)
        return super().form_valid(form)

class ExamUpdateView(ExamOwnerRequiredMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'dashboard/exam_form_custom.html'
    success_url = reverse_lazy('teacher_dashboard')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['section_formset'] = ExamSectionFormSet(self.request.POST, instance=self.object, prefix='sections')
        else:
            data['section_formset'] = ExamSectionFormSet(instance=self.object, prefix='sections')
        data['page_title'] = f'Chỉnh sửa: {self.object.title}'
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        section_formset = context['section_formset']
        with transaction.atomic():
            is_custom = form.cleaned_data.get('is_custom')
            if not is_custom:
                subject = form.cleaned_data.get('subject')
                form.instance.duration_minutes = EXAM_DURATION_MAP.get(subject, EXAM_DURATION_MAP['DEFAULT'])
            self.object = form.save()
            if is_custom:
                if section_formset.is_valid():
                    section_formset.instance = self.object
                    section_formset.save()
                else:
                    return self.form_invalid(form)
        return super().form_valid(form)

class ExamDeleteView(ExamOwnerRequiredMixin, DeleteView):
    model = Exam
    template_name = 'dashboard/exam_confirm_delete.html'
    success_url = reverse_lazy('teacher_dashboard')

class ReadingPassageUpdateView(TeacherRequiredMixin, UpdateView):
    model = ReadingPassage
    form_class = ReadingPassageForm
    template_name = 'dashboard/passage_form.html'
    
    def get_success_url(self):
        return reverse_lazy('exam_detail_teacher', kwargs={'pk': self.object.exam.pk})

    def get_queryset(self):
        return ReadingPassage.objects.filter(exam__owner=self.request.user)

@login_required
@user_passes_test(is_teacher)
def exam_detail_teacher(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if exam.owner != request.user:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")

    structured_exam = {}
    total_question_counter = 1
    
    if exam.is_custom:
        structure_config = {section.title: {'type': section.question_type, 'count': section.question_count} for section in exam.sections.all()}
    else:
        structure_key = SUBJECT_TO_STRUCTURE_KEY.get(exam.subject, 'NATURAL_SCIENCES')
        structure_config = EXAM_STRUCTURE.get(structure_key, {})

    passages = None
    if not exam.is_custom and exam.subject == 'TSA':
        passages = list(ReadingPassage.objects.filter(exam=exam).order_by('order'))
        if len(passages) < 2:
            for i in range(1, 3):
                ReadingPassage.objects.get_or_create(exam=exam, order=i, defaults={'title': f'Ngữ liệu {i}', 'content': f'Nhập nội dung ngữ liệu {i} tại đây.'})
            passages = list(ReadingPassage.objects.filter(exam=exam).order_by('order'))

    existing_questions = list(exam.questions.all().order_by('passage__order', 'order'))

    for section_title, config in structure_config.items():
        q_type = config['type']
        count = config['count']
        passage_order = config.get('passage_order')

        slots = []
        if passage_order:
            questions_of_this_type = [q for q in existing_questions if q.passage and q.passage.order == passage_order]
        else:
            questions_of_this_type = [q for q in existing_questions if q.question_type == q_type and not q.passage]

        for i in range(count):
            slot_data = {'display_order': total_question_counter, 'question': None, 'is_placeholder': True, 'order_in_type': i + 1}
            found_question = next((q for q in questions_of_this_type if q.order == i + 1), None)
            if found_question:
                slot_data['question'] = found_question
                slot_data['is_placeholder'] = False
            slots.append(slot_data)
            total_question_counter += 1
        
        structured_exam[section_title] = {'slots': slots, 'question_type_value': q_type, 'passage_order': passage_order}

    context = {
        'exam': exam,
        'structured_exam': structured_exam,
        'passages': passages,
    }
    return render(request, 'dashboard/exam_detail_teacher.html', context)

@login_required
@user_passes_test(is_teacher)
@transaction.atomic
def question_create_update(request, exam_pk, question_pk=None):
    """
    View này đã được viết lại hoàn toàn để xử lý việc tạo/cập nhật câu hỏi
    và tất cả các loại lựa chọn/formset một cách chính xác.
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
        
        # Nhận giá trị ban đầu từ URL để điền sẵn vào form
        initial_type = request.GET.get('type')
        initial_order = request.GET.get('order')
        if initial_type in Question.QuestionType.values:
            question.question_type = initial_type
        if initial_order and initial_order.isdigit():
            question.order = int(initial_order)

    # Giới hạn queryset cho trường passage trong form
    form = QuestionForm(instance=question)
    form.fields['passage'].queryset = ReadingPassage.objects.filter(exam=exam)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        form.fields['passage'].queryset = ReadingPassage.objects.filter(exam=exam)
        
        # Khởi tạo cả hai loại formset với dữ liệu POST và prefix riêng
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
            
    else: # GET request
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
    model = Question
    template_name = 'dashboard/question_confirm_delete.html'
    def get_success_url(self):
        return reverse_lazy('exam_detail_teacher', kwargs={'pk': self.object.exam.pk})

# --- VIEWS CHO HỌC SINH ---
class StudentExamListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = 'student/exam_list.html'
    context_object_name = 'exams'
    ordering = ['-created_at']
    login_url = 'login'

@login_required
def start_exam(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if exam.subject == Exam.SubjectType.TSA:
        return redirect('student_exam_take_section', pk=exam.pk, section_order=1)
    else:
        return redirect('student_exam_take', pk=exam.pk)

@login_required(login_url='login')
def student_exam_take(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    questions = exam.questions.prefetch_related('choices', 'match_pairs').all().order_by('order')

    if request.method == 'POST':
        final_score = 0.0
        points_map = {}
        if exam.is_custom:
            for section in exam.sections.all():
                points_map[section.question_type] = section.points_per_question
        
        for question in questions:
            q_id = str(question.id)
            points_for_this_question = 0.0
            
            if question.question_type == Question.QuestionType.SINGLE:
                selected_choice_id = request.POST.get(f'question{q_id}')
                if selected_choice_id and question.choices.filter(id=selected_choice_id, is_correct=True).exists():
                    points_for_this_question = points_map.get(question.question_type, 0.25) if exam.is_custom else 0.25
            
            elif question.question_type == Question.QuestionType.TRUE_FALSE:
                correct_sub_answers = 0
                for choice in question.choices.all():
                    user_answer = request.POST.get(f'question{q_id}_choice{choice.id}')
                    correct_answer = "Đúng" if choice.is_correct else "Sai"
                    if user_answer == correct_answer:
                        correct_sub_answers += 1
                if exam.is_custom:
                    points_for_this_question = points_map.get(question.question_type, 0.25) * correct_sub_answers
                else: # Thang điểm chuẩn
                    if correct_sub_answers == 1: points_for_this_question = 0.1
                    elif correct_sub_answers == 2: points_for_this_question = 0.25
                    elif correct_sub_answers == 3: points_for_this_question = 0.5
                    elif correct_sub_answers == 4: points_for_this_question = 1.0
            
            elif question.question_type == Question.QuestionType.FILL_IN_BLANK:
                user_answer = request.POST.get(f'question{q_id}', '').strip()
                correct_choice = question.choices.first()
                if correct_choice and user_answer.lower() == correct_choice.text.strip().lower():
                    if exam.is_custom:
                        points_for_this_question = points_map.get(question.question_type, 0.25)
                    else:
                        points_for_this_question = 0.5 if exam.subject == 'MATH' else 0.25
            
            final_score += points_for_this_question
        
        result = Result.objects.create(student=request.user, exam=exam, score=final_score, total=len(questions))
        return redirect('student_exam_result', pk=result.pk)
    
    context = {'exam': exam, 'questions': questions, 'duration_seconds': exam.duration_minutes * 60}
    return render(request, 'student/exam_take.html', context)

@login_required(login_url='login')
def student_exam_take_sectional(request, pk, section_order):
    exam = get_object_or_404(Exam, pk=pk)
    structure_config = EXAM_STRUCTURE.get('TSA', {})
    sections = []
    for i, (title, config) in enumerate(structure_config.items()):
        sections.append(type('obj', (object,), {'title': title, 'question_type': config['type'], 'question_count': config['count'], 'duration_minutes': config['duration'], 'order': i + 1, 'passage_order': config.get('passage_order')}))
    
    try:
        current_section = sections[section_order - 1]
    except IndexError:
        return HttpResponseForbidden("Phần thi không hợp lệ.")
    
    passage = None
    if current_section.passage_order:
        passage = ReadingPassage.objects.filter(exam=exam, order=current_section.passage_order).first()
        questions = passage.questions.all().order_by('order')[:current_section.question_count] if passage else []
    else:
        questions = exam.questions.filter(question_type=current_section.question_type, passage__isnull=True).order_by('order')[:current_section.question_count]
    
    session_key = f'exam_{pk}_answers'
    if request.method == 'GET' and section_order == 1:
        request.session[session_key] = {}

    if request.method == 'POST':
        section_answers = {k: v for k, v in request.POST.items() if k.startswith('question')}
        exam_answers = request.session.get(session_key, {})
        exam_answers[f'section_{section_order}'] = section_answers
        request.session[session_key] = exam_answers
        
        if section_order < len(sections):
            return redirect('student_exam_take_section', pk=pk, section_order=section_order + 1)
        else:
            final_score = 0
            all_answers_by_section = request.session.get(session_key, {})
            for sec_key, sec_answers in all_answers_by_section.items():
                for q_key, answer_id in sec_answers.items():
                    q_id = q_key.replace('question', '')
                    if Question.objects.filter(id=q_id, choices__id=answer_id, choices__is_correct=True).exists():
                        final_score += 1.0
            
            result = Result.objects.create(student=request.user, exam=exam, score=final_score, total=exam.questions.count())
            if session_key in request.session:
                del request.session[session_key]
            
            return redirect('student_exam_result', pk=result.pk)

    context = {'exam': exam, 'current_section': current_section, 'passage': passage, 'questions': questions, 'section_order': section_order, 'total_sections': len(sections), 'duration_seconds': current_section.duration_minutes * 60}
    return render(request, 'student/exam_take_sectional.html', context)

@login_required(login_url='login')
def student_exam_result(request, pk):
    result = get_object_or_404(Result, pk=pk, student=request.user)
    return render(request, 'student/exam_result.html', {'result': result})

class StudentResultHistoryView(LoginRequiredMixin, ListView):
    model = Result
    template_name = 'student/result_history.html'
    context_object_name = 'results'
    paginate_by = 10 # Hiển thị 10 kết quả mỗi trang
    login_url = 'login'

    def get_queryset(self):
        # Lấy tất cả kết quả của người dùng đang đăng nhập, sắp xếp mới nhất lên đầu
        queryset = Result.objects.filter(student=self.request.user).order_by('-submitted_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Lịch sử làm bài"
        return context