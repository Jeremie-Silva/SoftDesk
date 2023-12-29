# Generated by Django 5.0 on 2023-12-29 16:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soft_desk_api', '0005_project_created_time_project_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributor',
            name='age',
            field=models.PositiveSmallIntegerField(default=18),
        ),
        migrations.AlterField(
            model_name='project',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='authored_projects', to='soft_desk_api.contributor'),
        ),
        migrations.AlterField(
            model_name='project',
            name='contributors',
            field=models.ManyToManyField(related_name='projects', to='soft_desk_api.contributor'),
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('T', 'TO DO'), ('I', 'In Progress'), ('F', 'Finished')], default='T', max_length=100)),
                ('priority', models.CharField(blank=True, choices=[('L', 'LOW'), ('M', 'MEDIUM'), ('H', 'HIGH')], max_length=100)),
                ('label', models.CharField(blank=True, choices=[('B', 'BUG'), ('F', 'FEATURE'), ('T', 'TASK')], max_length=100)),
                ('assigned_contributor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_issues', to='soft_desk_api.contributor')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='issues', to='soft_desk_api.project')),
            ],
        ),
    ]
