# Generated by Django 5.2.4 on 2025-07-26 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizapp', '0010_readingpassage_question_passage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readingpassage',
            name='content',
            field=models.TextField(verbose_name='Nội dung Ngữ liệu'),
        ),
        migrations.AlterField(
            model_name='readingpassage',
            name='order',
            field=models.PositiveIntegerField(default=1, verbose_name='Thứ tự Ngữ liệu (1 hoặc 2)'),
        ),
        migrations.AlterField(
            model_name='readingpassage',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Tiêu đề Ngữ liệu'),
        ),
    ]
