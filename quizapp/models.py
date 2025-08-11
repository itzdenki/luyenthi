import string
import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _

def generate_exam_code():
    length = 6
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if Exam.objects.filter(code=code).count() == 0:
            break
    return code

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Học sinh'
        TEACHER = 'TEACHER', 'Giáo viên'
    
    first_name = models.CharField(_("Họ và Tên"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=True, editable=False)
    email = models.EmailField(_("email address"), unique=True)

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STUDENT)
    school = models.CharField(max_length=255, blank=True, verbose_name="Trường")
    school_class = models.CharField(max_length=50, blank=True, verbose_name="Lớp")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Ngày Sinh")
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    
    def __str__(self): return self.username

class Exam(models.Model):
    class SubjectType(models.TextChoices):
        MATH = 'MATH', 'Toán'
        PHYSICS = 'PHYSICS', 'Vật lý'
        CHEMISTRY = 'CHEMISTRY', 'Hóa học'
        BIOLOGY = 'BIOLOGY', 'Sinh học'
        HISTORY = 'HISTORY', 'Lịch sử'
        GEOGRAPHY = 'GEOGRAPHY', 'Địa lí'
        CIVIC_EDUCATION = 'CIVIC_EDUCATION', 'Giáo dục công dân'
        ENGLISH = 'ENGLISH', 'Tiếng Anh'
        TSA = 'TSA', 'Đánh giá tư duy (TSA)'
        OTHER = 'OTHER', 'Môn khác'

    class Visibility(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Công khai'
        PRIVATE = 'PRIVATE', 'Riêng tư (yêu cầu mã)'

    title = models.CharField(max_length=255, verbose_name="Tiêu đề kỳ thi")
    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        verbose_name="Chế độ hiển thị"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exams')
    subject = models.CharField(max_length=20, choices=SubjectType.choices, default=SubjectType.OTHER, verbose_name="Môn học (cho cấu trúc chuẩn)")
    duration_minutes = models.PositiveIntegerField(default=50, verbose_name="Thời gian làm bài (phút)")
    is_custom = models.BooleanField(default=False, verbose_name="Cấu trúc tùy chỉnh")
    code = models.CharField(max_length=8, unique=True, blank=True, default=generate_exam_code, verbose_name="Mã bài thi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta: ordering = ['-created_at']
    def __str__(self): return self.title

class ReadingPassage(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='passages')
    title = models.CharField(max_length=255, verbose_name="Tiêu đề Ngữ liệu")
    content = models.TextField(verbose_name="Nội dung Ngữ liệu")
    order = models.PositiveIntegerField(default=1, verbose_name="Thứ tự Ngữ liệu (1 hoặc 2)")
    class Meta:
        ordering = ['order']
        unique_together = ('exam', 'order')
    def __str__(self): return f"{self.title} - {self.exam.title}"

class Question(models.Model):
    class QuestionType(models.TextChoices):
        SINGLE = 'SINGLE', 'Trắc nghiệm - Chọn 1'
        MULTIPLE = 'MULTIPLE', 'Trắc nghiệm - Chọn nhiều'
        TRUE_FALSE = 'TRUE_FALSE', 'Đúng / Sai'
        FILL_IN_BLANK = 'FILL_IN_BLANK', 'Điền vào chỗ trống'
        MATCHING = 'MATCHING', 'Ghép đôi'

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name="Nội dung câu hỏi / Hướng dẫn")
    question_type = models.CharField(max_length=20, choices=QuestionType.choices, default=QuestionType.SINGLE, verbose_name="Loại câu hỏi")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự trong phần")
    passage = models.ForeignKey(ReadingPassage, on_delete=models.CASCADE, related_name='questions', null=True, blank=True, verbose_name="Ngữ liệu Đọc hiểu (nếu có)")
    class Meta: ordering = ['order']
    def __str__(self): return f"{self.get_question_type_display()}: {self.text[:50]}..."

class ExamSection(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255, verbose_name="Tiêu đề phần")
    question_type = models.CharField(max_length=20, choices=Question.QuestionType.choices, verbose_name="Loại câu hỏi")
    question_count = models.PositiveIntegerField(default=10, verbose_name="Số lượng câu")
    points_per_question = models.FloatField(default=0.25, verbose_name="Điểm mỗi câu")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự phần")
    class Meta: ordering = ['order']
    def __str__(self): return f"Phần {self.order}: {self.title} ({self.exam.title})"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500, verbose_name="Nội dung lựa chọn / Đáp án")
    is_correct = models.BooleanField(default=False, verbose_name="Là đáp án đúng?")
    def __str__(self): return self.text

class MatchPair(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='match_pairs')
    prompt = models.CharField(max_length=255, verbose_name="Vế ghép (Prompt)")
    answer = models.CharField(max_length=255, verbose_name="Vế trả lời (Answer)")
    def __str__(self): return f"{self.prompt} -> {self.answer}"

class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0, verbose_name="Điểm số")
    total = models.IntegerField(verbose_name="Tổng số câu")

    submission = models.JSONField(null=True, blank=True, verbose_name="Bài làm của học sinh")
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Kết quả của {self.student.username} cho {self.exam.title}"