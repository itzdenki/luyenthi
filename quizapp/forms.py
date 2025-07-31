from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from .models import User, Exam, Question, Choice, MatchPair, ExamSection, ReadingPassage

class CustomUserCreationForm(UserCreationForm):
    # Định nghĩa các trường mới cho form
    first_name = forms.CharField(max_length=150, required=True, label="Họ và Tên")
    email = forms.EmailField(required=True, label="Email")
    phone_number = forms.CharField(max_length=15, required=False, label="Số điện thoại")
    school = forms.CharField(max_length=255, required=False, label="Trường")
    school_class = forms.CharField(max_length=50, required=False, label="Lớp")
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), 
        required=False, 
        label="Ngày Sinh"
    )
    role = forms.ChoiceField(choices=User.Role.choices, label="Bạn là")

    class Meta(UserCreationForm.Meta):
        model = User
        # Chỉ định các trường sẽ được render bởi form, username sẽ được xử lý tự động
        fields = ("first_name", "email", 'phone_number', "school", "school_class", "date_of_birth", "role")

    def save(self, commit=True):
        user = super().save(commit=False)
        # Tự động gán username bằng email để đăng nhập
        user.username = self.cleaned_data["email"]
        # Gán các trường tùy chỉnh
        user.first_name = self.cleaned_data["first_name"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.school = self.cleaned_data["school"]
        user.school_class = self.cleaned_data["school_class"]
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'is_custom', 'subject', 'duration_minutes', 'description']
        labels = {
            'title': 'Tiêu đề bài thi',
            'is_custom': 'Sử dụng cấu trúc tùy chỉnh?',
            'subject': 'Môn học (áp dụng cho cấu trúc chuẩn)',
            'duration_minutes': 'Thời gian làm bài (phút)',
            'description': 'Mô tả',
        }

class ReadingPassageForm(forms.ModelForm):
    class Meta:
        model = ReadingPassage
        fields = ['title', 'content']
        labels = {
            'title': 'Tiêu đề Ngữ liệu',
            'content': 'Nội dung chi tiết',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'order', 'passage']
        labels = {
            'text': 'Nội dung câu hỏi / Hướng dẫn',
            'question_type': 'Loại câu hỏi',
            'order': 'Thứ tự trong phần',
            'passage': 'Ngữ liệu Đọc hiểu (chỉ dành cho TSA)',
        }
        widgets = {'text': forms.Textarea(attrs={'rows': 3})}

ChoiceFormSet = inlineformset_factory(
    Question, Choice,
    fields=('text', 'is_correct'),
    extra=1, can_delete=True,
    widgets={'text': forms.TextInput(attrs={'class': 'form-control'})}
)

MatchPairFormSet = inlineformset_factory(
    Question, MatchPair,
    fields=('prompt', 'answer'),
    extra=1, can_delete=True,
    widgets={
        'prompt': forms.TextInput(attrs={'class': 'form-control'}),
        'answer': forms.TextInput(attrs={'class': 'form-control'}),
    }
)

ExamSectionFormSet = inlineformset_factory(
    Exam, ExamSection,
    fields=('title', 'question_type', 'question_count', 'points_per_question', 'order'),
    extra=1, can_delete=True,
    widgets={
        'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tiêu đề phần, ví dụ: Trắc nghiệm'}),
        'question_type': forms.Select(attrs={'class': 'form-control'}),
        'question_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        'points_per_question': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.05', 'min': '0'}),
        'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
    }
)