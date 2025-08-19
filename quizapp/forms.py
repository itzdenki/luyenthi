from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from .models import User, Exam, Question, Choice, MatchPair, ExamSection, ReadingPassage
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label=_("Họ và Tên"))
    email = forms.EmailField(required=True, label=_("Email"))
    phone_number = forms.CharField(max_length=15, required=False, label=_("Số điện thoại"))
    school = forms.CharField(max_length=255, required=False, label=_("Trường"))
    school_class = forms.CharField(max_length=50, required=False, label=_("Lớp"))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label=_("Ngày Sinh"))
    role = forms.ChoiceField(choices=User.Role.choices, label=_("Bạn là"))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "email", "phone_number", "school", "school_class", "date_of_birth", "role")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.school = self.cleaned_data["school"]
        user.school_class = self.cleaned_data["school_class"]
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user

class UserInfoUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'phone_number', 'school', 'school_class', 'date_of_birth']
        labels = {'first_name': _('Họ và Tên'),'email': _('Email (không thể thay đổi)'),'phone_number': _('Số điện thoại'),'school': _('Trường'),'school_class': _('Lớp'),'date_of_birth': _('Ngày Sinh')}
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'}), 'email': forms.EmailInput(attrs={'readonly': True, 'style': 'background-color: var(--border);'})}

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'visibility', 'is_custom', 'subject', 'duration_minutes', 'description']
        labels = {'title': _('Tiêu đề bài thi'),'visibility': _('Chế độ hiển thị'),'is_custom': _('Sử dụng cấu trúc tùy chỉnh?'),'subject': _('Môn học (áp dụng cho cấu trúc chuẩn)'),'duration_minutes': _('Thời gian làm bài (phút)'),'description': _('Mô tả')}
        widgets = {'visibility': forms.RadioSelect}

class ReadingPassageForm(forms.ModelForm):
    class Meta:
        model = ReadingPassage
        fields = ['title', 'content']
        labels = {'title': _('Tiêu đề Ngữ liệu'), 'content': _('Nội dung chi tiết')}
        widgets = {'content': forms.Textarea(attrs={'rows': 20})}

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'order', 'passage']
        labels = {'text': _('Nội dung câu hỏi / Hướng dẫn'), 'question_type': _('Loại câu hỏi'), 'order': _('Thứ tự trong phần'), 'passage': _('Ngữ liệu Đọc hiểu (chỉ dành cho TSA)')}
        widgets = {'text': forms.Textarea(attrs={'rows': 3})}

class ExamCodeForm(forms.Form):
    code = forms.CharField(label="", max_length=8, widget=forms.TextInput(attrs={'placeholder': _('Nhập mã bài thi tại đây...'), 'style': 'text-transform: uppercase;'}))

class JsonImportForm(forms.Form):
    json_file = forms.FileField(label=_("Chọn file .json"))
    
ChoiceFormSet = inlineformset_factory(Question, Choice, fields=('text', 'is_correct'), extra=1, can_delete=True, widgets={'text': forms.TextInput(attrs={'class': 'form-control'})})
MatchPairFormSet = inlineformset_factory(Question, MatchPair, fields=('prompt', 'answer'), extra=1, can_delete=True, widgets={'prompt': forms.TextInput(attrs={'class': 'form-control'}), 'answer': forms.TextInput(attrs={'class': 'form-control'})})
ExamSectionFormSet = inlineformset_factory(Exam, ExamSection, fields=('title', 'question_type', 'question_count', 'points_per_question', 'order'), extra=1, can_delete=True, widgets={'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Tiêu đề phần, ví dụ: Trắc nghiệm')}), 'question_type': forms.Select(attrs={'class': 'form-control'}), 'question_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}), 'points_per_question': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.05', 'min': '0'}), 'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})})

