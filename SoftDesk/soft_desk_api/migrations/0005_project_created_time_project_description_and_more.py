# Generated by Django 5.0 on 2023-12-29 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soft_desk_api', '0004_remove_contributor_username_project_author_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, default='2023-12-29 15:30:00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='description',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='project',
            name='type',
            field=models.CharField(blank=True, choices=[('BE', 'Back-End'), ('FE', 'Front-End'), ('IOS', 'iOS'), ('AND', 'Android')], max_length=100),
        ),
    ]