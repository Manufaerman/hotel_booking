# Generated by Django 5.0.6 on 2024-10-16 12:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('number', models.IntegerField()),
                ('category', models.CharField(choices=[('ONE', 'Design apartment of a room with air conditioning'), ('NAC', 'Double bedroom without air conditioning'), ('3AC', 'Full three bedroom apartment with air conditioning'), ('TWO', 'Full two bedroom apartment without air conditioning'), ('YAC', 'double room with air conditioning')], max_length=2000)),
                ('bed', models.IntegerField()),
                ('capacity', models.IntegerField()),
                ('image', models.ImageField(default='img/room/default.jpg', upload_to='img/room')),
                ('image1', models.ImageField(default='img/room/default.jpg', upload_to='img/room')),
                ('image2', models.ImageField(default='img/room/default.jpg', upload_to='img/room')),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(blank=True, null=True)),
                ('date_price', models.DateField()),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotel.room')),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotel.price')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotel.room')),
            ],
        ),
    ]