# Generated by Django 4.1.3 on 2023-11-20 16:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_payment_delete_soldcommodity_alter_comment_options_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Payment',
        ),
    ]
