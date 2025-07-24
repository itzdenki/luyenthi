# quizapp/forms.py

from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # Thêm các trường bạn muốn hiển thị trong form đăng ký
        # Trường 'role' sẽ được thêm vào đây
        fields = ('username', 'email', 'role')

    # Thêm trường role vào form
    role = forms.ChoiceField(choices=User.Role.choices)