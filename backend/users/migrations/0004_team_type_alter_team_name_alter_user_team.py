# Generated by Django 5.2.3 on 2025-06-17 13:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_team_name_alter_user_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='type',
            field=models.CharField(choices=[('KANAT', 'Kanat Takımı'), ('GOVDE', 'Gövde Takımı'), ('KUYRUK', 'Kuyruk Takımı'), ('AVIYONIK', 'Aviyonik Takımı'), ('MONTAJ', 'Montaj Takımı')], default='KANAT', max_length=10, verbose_name='Takım Tipi'),
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Takım Adı'),
        ),
        migrations.AlterField(
            model_name='user',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='users.team', verbose_name='Takım'),
        ),
    ]
