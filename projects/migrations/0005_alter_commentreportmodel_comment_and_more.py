# Generated by Django 4.2.6 on 2023-10-29 16:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_alter_commentreportmodel_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentreportmodel',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reportedComment', to='projects.commentsmodel'),
        ),
        migrations.AlterField(
            model_name='commentreportmodel',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commentReports', to='projects.projectsmodel'),
        ),
    ]
