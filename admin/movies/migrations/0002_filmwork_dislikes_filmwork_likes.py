# Generated by Django 4.2.14 on 2024-08-24 16:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="filmwork",
            name="dislikes",
            field=models.SmallIntegerField(
                default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name="dislikes"
            ),
        ),
        migrations.AddField(
            model_name="filmwork",
            name="likes",
            field=models.SmallIntegerField(
                default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name="likes"
            ),
        ),
    ]
