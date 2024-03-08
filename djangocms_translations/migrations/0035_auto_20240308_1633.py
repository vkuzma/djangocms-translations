# Generated by Django 3.2.25 on 2024-03-08 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_translations', '0034_auto_20240308_0839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translationdirective',
            name='master_language',
            field=models.CharField(max_length=10, verbose_name='master language'),
        ),
        migrations.AlterField(
            model_name='translationdirectiveinline',
            name='language',
            field=models.CharField(editable=False, max_length=10, verbose_name='language'),
        ),
    ]
