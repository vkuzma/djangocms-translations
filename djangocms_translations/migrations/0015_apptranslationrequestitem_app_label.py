# Generated by Django 3.2.20 on 2023-08-14 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_translations', '0014_auto_20230814_1727'),
    ]

    operations = [
        migrations.AddField(
            model_name='apptranslationrequestitem',
            name='app_label',
            field=models.CharField(default='people', max_length=100, verbose_name='App label'),
            preserve_default=False,
        ),
    ]