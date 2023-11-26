# Generated by Django 4.1.3 on 2023-11-24 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

  dependencies = [
      ('payment', '0001_initial'),
  ]

  operations = [
      migrations.CreateModel(
          name='Replenishment',
          fields=[
              ('id', models.BigAutoField(auto_created=True,
               primary_key=True, serialize=False, verbose_name='ID')),
              ('amount', models.DecimalField(decimal_places=2, max_digits=9)),
              ('payment', models.OneToOneField(
                  null=True, on_delete=django.db.models.deletion.SET_NULL, to='payment.payment')),
          ],
      ),
  ]