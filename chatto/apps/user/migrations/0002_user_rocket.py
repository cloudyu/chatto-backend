# Generated by Django 2.1.5 on 2019-09-11 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='rocket',
            field=models.CharField(default='', editable=False, max_length=64),
            preserve_default=False,
        ),
    ]