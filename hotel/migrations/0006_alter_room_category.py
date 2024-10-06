# Generated by Django 5.0.6 on 2024-07-25 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0005_alter_room_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='category',
            field=models.CharField(choices=[('TWO', 'Full two bedroom apartment without air conditioning'), ('ONE', 'Design apartment of a room with air conditioning'), ('YAC', 'double room with air conditioning'), ('3AC', 'Full three bedroom apartment with air conditioning'), ('NAC', 'Double bedroom without air conditioning')], max_length=3),
        ),
    ]