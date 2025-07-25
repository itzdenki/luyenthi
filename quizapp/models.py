# quizapp/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# ... (Model User và Exam giữ nguyên) ...
class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Học sinh'
        TEACHER = 'TEACHER', 'Giáo viên'
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STUDENT)
    def __str__(self): return self.username

class Exam(models.Model):
    title = models.CharField(max_length=255, verbose_name="Tiêu đề kỳ thi")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return self.title


# =======================================================
# NÂNG CẤP MODEL QUESTION
# =======================================================
class Question(models.Model):
    """
    Mở rộng model Question để hỗ trợ nhiều loại câu hỏi.
    """
    class QuestionType(models.TextChoices):
        # Các loại cũ
        SINGLE = 'SINGLE', 'Trắc nghiệm - Chọn 1'
        MULTIPLE = 'MULTIPLE', 'Trắc nghiệm - Chọn nhiều'
        
        # Các loại mới
        TRUE_FALSE = 'TRUE_FALSE', 'Đúng / Sai'
        FILL_IN_BLANK = 'FILL_IN_BLANK', 'Điền vào chỗ trống'
        MATCHING = 'MATCHING', 'Ghép đôi'
        # Các loại khác có thể thêm sau...
        # ORDERING_WORD = 'ORDERING_WORD', 'Sắp xếp từ'
        # ORDERING_SENTENCE = 'ORDERING_SENTENCE', 'Sắp xếp câu'

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name="Nội dung câu hỏi / Hướng dẫn")
    
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE,
        verbose_name="Loại câu hỏi"
    )
    
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_question_type_display()}: {self.text[:50]}..."

# =======================================================
# MODEL CHO LỰA CHỌN (TRẮC NGHIỆM, ĐÚNG/SAI, ĐIỀN KHUYẾT)
# =======================================================
class Choice(models.Model):
    """
    Model này giờ sẽ phục vụ cho:
    - Trắc nghiệm (SINGLE, MULTIPLE)
    - Đúng/Sai (TRUE_FALSE)
    - Điền khuyết (FILL_IN_BLANK): trường 'text' sẽ chứa đáp án đúng.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500, verbose_name="Nội dung lựa chọn / Đáp án")
    is_correct = models.BooleanField(default=False, verbose_name="Là đáp án đúng?")

    def __str__(self):
        return self.text

# =======================================================
# MODEL MỚI CHO CÂU HỎI GHÉP ĐÔI
# =======================================================
class MatchPair(models.Model):
    """
    Mỗi đối tượng của model này là một cặp "Vế A - Vế B" cho câu hỏi ghép đôi.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='match_pairs')
    prompt = models.CharField(max_length=255, verbose_name="Vế ghép (Prompt)")
    answer = models.CharField(max_length=255, verbose_name="Vế trả lời (Answer)")

    def __str__(self):
        return f"{self.prompt} -> {self.answer}"

class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Kết quả của {self.student.username} cho {self.exam.title}"