# Generated by Django 4.0.2 on 2022-03-03 18:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_alter_question_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 3, 19, 51, 15, 280476), verbose_name='date published'),
        ),
    ]
