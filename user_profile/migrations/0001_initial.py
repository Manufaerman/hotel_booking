# Generated by Django 4.2.5 on 2024-06-18 09:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('phone', models.IntegerField(blank=True)),
                ('id', models.IntegerField(blank=True)),
                ('address', models.CharField(blank=True, max_length=150)),
                ('cp', models.IntegerField(blank=True)),
                ('city', models.CharField(blank=True, max_length=150)),
                ('country', models.CharField(blank=True, max_length=150)),
                ('birthday', models.DateField(blank=True)),
            ],
        ),
    ]