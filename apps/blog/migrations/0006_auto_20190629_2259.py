# Generated by Django 2.0.3 on 2019-06-29 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20190629_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='img',
            field=models.ImageField(blank=True, default='/static/images/summary.jpg', null=True, upload_to='media'),
        ),
        migrations.AlterField(
            model_name='carousel',
            name='img',
            field=models.ImageField(blank=True, default='/static/images/summary.jpg', null=True, upload_to='media'),
        ),
    ]