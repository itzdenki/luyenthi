from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language # SỬA LỖI: Import view có sẵn của Django

# Các URL không cần tiền tố ngôn ngữ
urlpatterns = [
    path('admin/', admin.site.urls),
    # SỬA LỖI: Dùng view set_language có sẵn của Django
    path('i18n/', include('django.conf.urls.i18n')),
]

# Các URL sẽ có tiền tố ngôn ngữ
urlpatterns += i18n_patterns(
    path('', include('quizapp.urls')),
)