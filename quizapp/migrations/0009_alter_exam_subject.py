# Generated by Django 5.2.4 on 2025-07-26 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizapp', '0008_alter_exam_subject_alter_question_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='subject',
            field=models.CharField(choices=[('MATH', 'Toán'), ('PHYSICS', 'Vật lý'), ('CHEMISTRY', 'Hóa học'), ('BIOLOGY', 'Sinh học'), ('HISTORY', 'Lịch sử'), ('GEOGRAPHY', 'Địa lí'), ('CIVIC_EDUCATION', 'Giáo dục công dân'), ('ENGLISH', 'Tiếng Anh'), ('OTHER', 'Môn khác'), ('TSA', 'Đánh giá tư duy')], default='OTHER', max_length=20, verbose_name='Môn học (cho cấu trúc chuẩn)'),
        ),
    ]
