# Generated by Django 5.1.1 on 2025-03-14 15:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Administrator",
            fields=[
                ("admin_id", models.AutoField(primary_key=True, serialize=False)),
                ("admin_psw", models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("customer_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=10)),
                ("email", models.EmailField(max_length=20)),
                ("password", models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name="Poll",
            fields=[
                ("poll_id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("cut_off", models.DurationField()),
                ("active", models.BooleanField(default=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polls",
                        to="polls.customer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Option",
            fields=[
                ("option_id", models.AutoField(primary_key=True, serialize=False)),
                ("content", models.CharField(max_length=20)),
                ("count", models.IntegerField(default=0)),
                (
                    "poll",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="options",
                        to="polls.poll",
                    ),
                ),
            ],
        ),
    ]
