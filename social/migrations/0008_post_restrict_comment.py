# Generated by Django 3.0.3 on 2020-03-30 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0007_comment_reply'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='restrict_comment',
            field=models.BooleanField(default=False),
        ),
    ]
