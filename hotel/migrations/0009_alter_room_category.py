# Generated by Django 5.0.6 on 2024-10-12 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0008_alter_room_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='category',
            field=models.CharField(choices=[('3AC', 'Full three bedroom apartment with air conditioning'), ('YAC', 'double room with air conditioning'), ('TWO', 'Full two bedroom apartment without air conditioning'), ('NAC', 'Double bedroom without air conditioning'), ('ONE', 'Design apartment of a room with air conditioning')], max_length=3),
        ),
    ]
