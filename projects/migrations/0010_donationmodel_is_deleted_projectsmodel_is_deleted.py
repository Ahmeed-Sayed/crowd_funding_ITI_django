# Generated by Django 4.2.7 on 2024-01-16 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_donationmodel_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationmodel',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='projectsmodel',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
