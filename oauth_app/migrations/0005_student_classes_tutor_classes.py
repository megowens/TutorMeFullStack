# Generated by Django 4.1.6 on 2023-03-18 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_app', '0004_remove_student_verify_student_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='classes',
            field=models.TextField(default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='tutor',
            name='classes',
            field=models.TextField(default='', max_length=1000),
        ),
    ]
