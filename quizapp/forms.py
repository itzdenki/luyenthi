# quizapp/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Exam, Question, Choice, MatchPair
from django.forms import inlineformset_factory

# --- Form Đăng ký (đã có từ trước) ---
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')

    role = forms.ChoiceField(choices=User.Role.choices)

# =======================================================
# 1. ModelForm cho Exam
# =======================================================
class ExamForm(forms.ModelForm):
    class Meta:
        # Liên kết form này với model Exam
        model = Exam
        
        # Chọn các trường từ model Exam sẽ hiển thị trong form
        # Chúng ta không cần trường 'owner' vì nó sẽ được gán tự động trong view
        fields = ['title', 'description']

        # Tùy chỉnh nhãn (label) và widget cho các trường
        labels = {
            'title': 'Tiêu đề bài thi',
            'description': 'Mô tả chi tiết',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}), # Hiển thị description như một textarea
        }

# =======================================================
# 2. ModelForm cho Question
# =======================================================
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        
        # THÊM 'question_type' VÀO ĐÂY
        fields = ['text', 'question_type', 'order']
        
        labels = {
            'text': 'Nội dung câu hỏi / Hướng dẫn',
            'question_type': 'Loại câu hỏi',
            'order': 'Thứ tự hiển thị',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

ChoiceFormSet = inlineformset_factory(
    Question,  # Model cha
    Choice,    # Model con
    fields=('text', 'is_correct'), # Các trường cần hiển thị
    extra=1, # Bắt đầu với 1 form trống
    can_delete=True, # Cho phép xóa các lựa chọn
    widgets={
        'text': forms.TextInput(attrs={'class': 'form-control'}),
    }
)

# Formset cho MatchPair (Ghép đôi)
MatchPairFormSet = inlineformset_factory(
    Question,
    MatchPair,
    fields=('prompt', 'answer'),
    extra=1,
    can_delete=True,
    widgets={
        'prompt': forms.TextInput(attrs={'class': 'form-control'}),
        'answer': forms.TextInput(attrs={'class': 'form-control'}),
    }
)