# quizapp/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Exam, Question, Choice

# --- Đăng ký Model User tùy chỉnh ---

class CustomUserAdmin(UserAdmin):
    # Thêm trường 'role' vào fieldsets để hiển thị trên trang chi tiết người dùng
    # Chúng ta kế thừa các fieldsets mặc định và thêm của mình vào
    fieldsets = UserAdmin.fieldsets + (
        ('Phân quyền tùy chỉnh', {'fields': ('role',)}),
    )
    
    # Thêm trường 'role' vào add_fieldsets để hiển thị trên trang tạo mới người dùng
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )
    
    # Thêm 'role' vào list_display để hiển thị ở danh sách người dùng
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')

# Đăng ký model User của bạn với class CustomUserAdmin
admin.site.register(User, CustomUserAdmin)


# --- Đăng ký các model khác như cũ ---

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('text', 'exam', 'order')

admin.site.register(Exam)
admin.site.register(Question, QuestionAdmin)