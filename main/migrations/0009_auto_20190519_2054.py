# Generated by Django 2.2 on 2019-05-19 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_notification_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='running',
            field=models.IntegerField(default=0),
        ),
    ]
