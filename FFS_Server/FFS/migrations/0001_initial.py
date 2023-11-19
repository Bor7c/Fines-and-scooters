# Generated by Django 4.2.4 on 2023-11-19 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fines',
            fields=[
                ('fine_id', models.AutoField(primary_key=True, serialize=False)),
                ('picture_url', models.CharField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=70, null=True, unique=True)),
                ('price', models.CharField(blank=True, null=True)),
                ('text', models.CharField(blank=True, null=True)),
                ('fine_status', models.CharField(default='действует', max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('login', models.CharField(max_length=255, unique=True, verbose_name='Логин')),
                ('password', models.CharField(max_length=255, verbose_name='Пароль')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Является ли пользователь менеджером?')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='Является ли пользователь админом?')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Breaches',
            fields=[
                ('breach_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('closed_date', models.DateTimeField(blank=True, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('formated_date', models.DateTimeField(blank=True, null=True)),
                ('breach_status', models.CharField(default='черновик', max_length=20)),
                ('moder_id', models.IntegerField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='FFS.users')),
            ],
        ),
        migrations.CreateModel(
            name='ConfOfFines',
            fields=[
                ('cofid', models.BigAutoField(primary_key=True, serialize=False)),
                ('fine_desc', models.CharField(blank=True, max_length=400, null=True)),
                ('breach', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FFS.breaches')),
                ('fine', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FFS.fines')),
            ],
            options={
                'unique_together': {('fine', 'breach')},
            },
        ),
    ]
