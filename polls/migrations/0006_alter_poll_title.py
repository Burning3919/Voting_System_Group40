# Generated by Django 5.1.1 on 2025-03-15 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0005_poll_cut_off"),
    ]

    operations = [
        migrations.AlterField(
            model_name="poll",
            name="title",
            field=models.CharField(max_length=100),
        ),
    ]
