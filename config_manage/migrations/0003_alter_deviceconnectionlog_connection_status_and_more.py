# Generated by Django 5.0.8 on 2024-09-29 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config_manage', '0002_deviceconnectionlog_connection_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceconnectionlog',
            name='connection_status',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='deviceconnectionlog',
            name='hostname',
            field=models.CharField(max_length=255),
        ),
    ]
