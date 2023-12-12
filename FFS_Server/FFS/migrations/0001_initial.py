# Generated by Django 4.2.4 on 2023-12-01 21:47

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fines',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, default='images/default.jpg', null=True, upload_to='')),
                ('title', models.CharField(blank=True, max_length=70, null=True)),
                ('price', models.CharField(blank=True, null=True)),
                ('text', models.CharField(blank=True, null=True)),
                ('status', models.IntegerField(choices=[(1, 'Действует'), (2, 'Удалена')], default=1, verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'Штраф',
                'verbose_name_plural': 'Штрафы',
            },
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(unique=True)),
                ('is_moderator', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
        ),
        migrations.CreateModel(
            name='Breaches',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(blank=True, default=datetime.datetime(2023, 12, 1, 21, 47, 33, 771298, tzinfo=datetime.timezone.utc), null=True)),
                ('formated_date', models.DateTimeField(blank=True, null=True)),
                ('closed_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.IntegerField(choices=[(1, 'Введён'), (2, 'В работе'), (3, 'Завершён'), (4, 'Отменён'), (5, 'Удалён')], default=1, verbose_name='Статус')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Нарушение',
                'verbose_name_plural': 'Нарушения',
            },
        ),
        migrations.CreateModel(
            name='ConfOfFines',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fine_desc', models.CharField(blank=True, max_length=400, null=True)),
                ('breach', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='FFS.breaches')),
                ('fine', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='FFS.fines')),
            ],
            options={
                'verbose_name': 'Штраф-нарушение',
                'verbose_name_plural': 'Штрафы-нарушение',
                'unique_together': {('fine', 'breach')},
            },
        ),
    ]
