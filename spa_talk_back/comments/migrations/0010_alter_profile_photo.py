# Generated by Django 5.1.4 on 2024-12-31 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0009_alter_profile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='user_photos/', verbose_name='Profile Photo'),
        ),
    ]