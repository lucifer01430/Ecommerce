# Generated by Django 5.1.5 on 2025-04-12 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_cartitems_color_variant_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitems',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
