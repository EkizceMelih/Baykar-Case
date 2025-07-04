# Generated by Django 5.2.3 on 2025-06-17 12:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assembly', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('KANAT', 'Kanat'), ('GOVDE', 'Gövde'), ('KUYRUK', 'Kuyruk'), ('AVIYONIK', 'Aviyonik')], max_length=10, verbose_name='Parça Tipi')),
                ('aircraft_model', models.CharField(choices=[('TB2', 'TB2'), ('TB3', 'TB3'), ('AKINCI', 'Akıncı'), ('KIZILELMA', 'Kızilelma')], max_length=10, verbose_name='Uyumlu Hava Aracı Modeli')),
                ('serial_number', models.CharField(blank=True, editable=False, max_length=100, unique=True, verbose_name='Seri Numarası')),
                ('status', models.CharField(choices=[('AVAILABLE', 'Mevcut'), ('USED', 'Kullanıldı'), ('RECYCLED', 'Geri Dönüşümde')], default='AVAILABLE', max_length=20, verbose_name='Durum')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_parts', to=settings.AUTH_USER_MODEL)),
                ('used_in_aircraft', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parts', to='assembly.aircraft')),
            ],
            options={
                'verbose_name': 'Parça',
                'verbose_name_plural': 'Parçalar',
            },
        ),
    ]
