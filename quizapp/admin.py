# quizapp/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Exam, Question, Choice, MatchPair # Import MatchPair

# --- Custom User Admin ---
class CustomUserAdmin(UserAdmin):
    # Cập nhật để hiển thị các trường mới trong trang admin
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('phone_number', 'school', 'school_class', 'date_of_birth', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin cá nhân', {'fields': ('first_name', 'phone_number', 'school', 'school_class', 'date_of_birth', 'role')}),
    )
    list_display = ('username', 'email', 'first_name', 'phone_number', 'is_staff', 'role')
    search_fields = ('username', 'first_name', 'email', 'phone_number')

# Đăng ký lại User với CustomUserAdmin
# admin.site.unregister(User) # Dòng này có thể gây lỗi nếu User chưa được đăng ký, nên comment lại nếu cần
admin.site.register(User, CustomUserAdmin)

# --- Inlines for Question Admin ---
# Các form con sẽ hiển thị bên trong trang chi tiết của Question

# Inline cho Choice (dùng cho Trắc nghiệm, Đúng/Sai, Điền khuyết)
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1 # Hiển thị 1 dòng trống để nhập liệu
    fields = ('text', 'is_correct')
    verbose_name = "Lựa chọn hoặc Đáp án"
    verbose_name_plural = "Các lựa chọn / Đáp án"

# Inline cho MatchPair (dùng cho Ghép đôi)
class MatchPairInline(admin.TabularInline):
    model = MatchPair
    extra = 1 # Hiển thị 1 dòng trống để nhập liệu
    fields = ('prompt', 'answer')
    verbose_name = "Cặp ghép"
    verbose_name_plural = "Các cặp để ghép"


# --- Question Admin ---
# Sử dụng decorator @admin.register để đăng ký model Question
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'question_type', 'order')
    list_filter = ('exam', 'question_type')
    search_fields = ('text', 'exam__title')
    
    # Phương thức quan trọng: Hiển thị form con (inline) phù hợp với loại câu hỏi
    def get_inlines(self, request, obj=None):
        """
        Ghi đè phương thức này để trả về inline chính xác.
        'obj' là đối tượng Question đang được chỉnh sửa.
        """
        if obj: # Nếu đang ở trang chỉnh sửa một câu hỏi đã có
            # Nếu là các loại câu hỏi dùng model Choice
            if obj.question_type in [Question.QuestionType.SINGLE, Question.QuestionType.MULTIPLE, Question.QuestionType.TRUE_FALSE, Question.QuestionType.FILL_IN_BLANK]:
                return [ChoiceInline]
            # Nếu là loại câu hỏi Ghép đôi
            elif obj.question_type == Question.QuestionType.MATCHING:
                return [MatchPairInline]
        return [] # Không hiển thị inline nào khi đang tạo mới câu hỏi


# --- Exam Admin ---
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    search_fields = ('title', 'owner__username')

# Lưu ý: Chúng ta thường không cần đăng ký các model inline (Choice, MatchPair)
# một cách độc lập trên trang admin, vì chúng đã được quản lý bên trong Question.
# admin.site.register(Choice)
# admin.site.register(MatchPair)
