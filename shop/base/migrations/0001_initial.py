# Generated by Django 4.1.3 on 2023-03-11 18:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('title', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('picture', models.ImageField(default='default.png', upload_to='categories')),
            ],
        ),
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('rating', models.FloatField(default=3)),
                ('adding_date', models.DateField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('picture', models.ImageField(default='default.png', upload_to='commodities')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.category')),
            ],
            options={
                'ordering': ['-rating'],
            },
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='SoldCommodity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('category', models.CharField(max_length=100)),
                ('manufacturer', models.CharField(max_length=100)),
                ('selling_date', models.DateField(auto_now_add=True)),
                ('username', models.CharField(max_length=100)),
            ],
            options={
                'permissions': (('can_form_report', 'can form report'),),
            },
        ),
        migrations.CreateModel(
            name='CommodityInCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.cart')),
                ('commodity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.commodity')),
            ],
        ),
        migrations.CreateModel(
            name='CommodityEvaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.PositiveIntegerField(default=3)),
                ('commodity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.commodity')),
                ('evaluator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='commodity',
            name='manufacturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.manufacturer'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=1000)),
                ('sending_datetime', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('commodity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.commodity')),
            ],
            options={
                'ordering': ['-sending_datetime'],
            },
        ),
    ]