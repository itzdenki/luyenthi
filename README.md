# 📚 Luyện Thi – Ứng dụng Trắc Nghiệm Ôn Tập

> Web app Django giúp tạo & làm bài tập trắc nghiệm, hướng tới nhu cầu ôn luyện thi THPT/ĐGNL.

---

## ✨ Tính năng nổi bật

* **Quản lý ngân hàng câu hỏi**: tạo, sửa, phân loại câu hỏi theo môn học & mức độ.
* **Sinh đề tự động**: tạo bài kiểm tra ngẫu nhiên hoặc theo chủ đề, giới hạn thời gian.
* **Chấm điểm tức thì**: tính điểm & hiển thị đáp án sau khi nộp bài.
* **Lưu lịch sử**: thống kê kết quả, bảng xếp hạng theo người dùng.
* **Giao diện Responsive**: HTML/CSS (Bootstrap) phù hợp cả desktop & mobile.

---

## 🏗️ Cấu trúc dự án (rút gọn)

```text
luyenthi/
├── quizproject/      # Cấu hình Django project
│   ├── settings.py
│   └── urls.py
├── quizapp/          # Django app chính (models, views, templates)
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── manage.py
└── db.sqlite3
```

---

## 🚀 Hướng dẫn cài đặt nhanh

> **Yêu cầu:** Python ≥ 3.10, Git, pip & virtualenv/venv

```bash
# 1. Sao chép mã nguồn
$ git clone https://github.com/itzdenki/luyenthi.git
$ cd luyenthi

# 2. Tạo và kích hoạt môi trường ảo
$ python -m venv venv
$ source venv/bin/activate    # Windows: venv\Scripts\activate

# 3. Cài phụ thuộc
$ pip install -r requirements.txt   # nếu chưa có hãy: pip install django==4.2

# 4. Khởi tạo cơ sở dữ liệu & tài khoản quản trị
$ python manage.py migrate
$ python manage.py createsuperuser   # tuỳ chọn

# 5. Chạy server cục bộ
$ python manage.py runserver

# Mở trình duyệt tại http://127.0.0.1:8000/
```

---

## ⚙️ Tuỳ chỉnh & Phát triển

| Tác vụ                     | Thao tác                                                 |
| -------------------------- | -------------------------------------------------------- |
| Thêm câu hỏi/đề thi        | Đăng nhập `/admin` ➜ Tạo `Category`, `Question`, `Quiz`  |
| Thay đổi thời gian làm bài | Sửa trường `duration` của model `Quiz`                   |
| Giao diện                  | Chỉnh template trong `quizapp/templates/` & static files |
| Kiểm thử                   | `python manage.py test`                                  |

### Docker (tuỳ chọn)

```bash
# Build image
$ docker build -t luyenthi .
# Chạy container
$ docker run -d -p 8000:8000 luyenthi
```

---

## 🤝 Đóng góp

1. Fork & tạo nhánh: `git checkout -b feature-awesome`
2. Commit: `git commit -m "Add awesome feature"`
3. Push: `git push origin feature-awesome`
4. Mở Pull Request.

---

## 📄 Giấy phép

Phát hành theo giấy phép **MIT** – tự do sử dụng cho mục đích học tập & cá nhân.

---

> Made with ❤️ & Django – Tham gia đóng góp để cùng cải tiến! 😉
