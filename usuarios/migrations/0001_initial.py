# Generated by Django 2.2.6 on 2019-12-09 11:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_afiliado', models.CharField(max_length=45, unique=True, verbose_name='Número de Afiliado')),
                ('fecha_nacimiento', models.DateField()),
                ('num_tel', models.CharField(max_length=11, verbose_name='Número de Telefono')),
                ('dni', models.CharField(max_length=45, verbose_name='DNI')),
                ('id_agente', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Agente',
                'verbose_name_plural': 'Agentes',
                'db_table': 'agente',
                'managed': True,
            },
        ),
    ]