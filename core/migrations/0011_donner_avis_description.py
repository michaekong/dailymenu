# Generated by Django 5.2.1 on 2025-06-17 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_donner_avis_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='donner_avis',
            name='description',
            field=models.TextField(default=True),
        ),
    ]
