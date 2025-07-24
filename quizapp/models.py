# In quizapp/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings # <-- THÊM DÒNG NÀY

# ==================================
# 1. Model User (mở rộng)
# ==================================
class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Học sinh'
        TEACHER = 'TEACHER', 'Giáo viên'

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STUDENT)

    def __str__(self):
        return self.username

# ==================================
# 2. Model Exam
# ==================================
class Exam(models.Model):
    title = models.CharField(max_length=255, verbose_name="Tiêu đề kỳ thi")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    
    # SỬA Ở ĐÂY: Dùng settings.AUTH_USER_MODEL thay vì 'User' trực tiếp
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='exams'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# Các model Question và Choice giữ nguyên vì chúng không liên kết trực tiếp đến User
# ==================================
# 3. Model Question
# ==================================
class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name="Nội dung câu hỏi")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Câu hỏi {self.order}: {self.text[:50]}..."

# ==================================
# 4. Model Choice
# ==================================
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500, verbose_name="Nội dung lựa chọn")
    is_correct = models.BooleanField(default=False, verbose_name="Là đáp án đúng?")

    def __str__(self):
        return self.text