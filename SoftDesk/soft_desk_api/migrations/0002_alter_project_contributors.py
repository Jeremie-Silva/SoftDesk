# Generated by Django 5.0 on 2024-01-05 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soft_desk_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='contributors',
            field=models.ManyToManyField(related_name='projects_contribution', to='soft_desk_api.contributor'),
        ),
    ]
